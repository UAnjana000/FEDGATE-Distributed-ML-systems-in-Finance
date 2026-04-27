param(
    [string]$Region = "ap-south-1",
    [string]$NamePrefix = "fedgate",
    [string]$PostgresPassword = "fedrisk"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-External {
    param(
        [scriptblock]$Command,
        [string]$ErrorMessage
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw $ErrorMessage
    }
}

function Invoke-WithRetry {
    param(
        [scriptblock]$Command,
        [string]$ErrorMessage,
        [int]$MaxAttempts = 3,
        [int]$DelaySeconds = 10
    )

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        & $Command
        if ($LASTEXITCODE -eq 0) {
            return
        }

        if ($attempt -lt $MaxAttempts) {
            Write-Host "Attempt $attempt failed. Retrying in $DelaySeconds seconds..."
            Start-Sleep -Seconds $DelaySeconds
        }
    }

    throw $ErrorMessage
}

function Get-TerraformPath {
    $terraformCommand = Get-Command terraform -ErrorAction SilentlyContinue
    if ($terraformCommand) {
        return $terraformCommand.Source
    }

    $wingetCandidates = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages") -Filter "Hashicorp.Terraform_*" -Directory -ErrorAction SilentlyContinue
    foreach ($candidate in $wingetCandidates) {
        $terraformExe = Join-Path $candidate.FullName "terraform.exe"
        if (Test-Path $terraformExe) {
            return $terraformExe
        }
    }

    throw "Terraform executable not found. Install terraform first."
}

function Ensure-EcrRepository {
    param(
        [string]$RepositoryName,
        [string]$Region
    )

    aws ecr describe-repositories --repository-names $RepositoryName --region $Region 1>$null 2>$null
    $repoExists = ($LASTEXITCODE -eq 0)

    if (-not $repoExists) {
        Invoke-External -Command { aws ecr create-repository --repository-name $RepositoryName --region $Region | Out-Null } -ErrorMessage "Failed to create ECR repository: $RepositoryName"
    }
}

Write-Host "Validating AWS identity..."
Invoke-External -Command { $script:accountId = aws sts get-caller-identity --query Account --output text } -ErrorMessage "Unable to read AWS identity."
if (-not $accountId) {
    throw "Unable to read AWS account id from configured profile."
}

$terraformPath = Get-TerraformPath
$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$terraformDir = (Resolve-Path (Join-Path $PSScriptRoot "terraform")).Path
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

$repositoryMap = @{
    "api-gateway"    = "$NamePrefix/api-gateway"
    "risk-engine"    = "$NamePrefix/risk-engine"
    "fl-orchestrator"= "$NamePrefix/fl-orchestrator"
    "alert-service"  = "$NamePrefix/alert-service"
    "web"            = "$NamePrefix/web"
}

Write-Host "Ensuring ECR repositories exist..."
foreach ($repoName in $repositoryMap.Values) {
    Ensure-EcrRepository -RepositoryName $repoName -Region $Region
}

$registry = "$accountId.dkr.ecr.$Region.amazonaws.com"
Write-Host "Logging in to ECR registry $registry ..."
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $registry | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Docker login to ECR failed. Check Docker daemon status and AWS auth."
}

Set-Location $rootDir

$apiImage = "$registry/$($repositoryMap["api-gateway"]):$timestamp"
$riskImage = "$registry/$($repositoryMap["risk-engine"]):$timestamp"
$flImage = "$registry/$($repositoryMap["fl-orchestrator"]):$timestamp"
$alertImage = "$registry/$($repositoryMap["alert-service"]):$timestamp"
$webImageBoot = "$registry/$($repositoryMap["web"]):$timestamp-bootstrap"

Write-Host "Building and pushing backend images..."
Invoke-External -Command { docker build -f services/api-gateway/Dockerfile -t $apiImage . } -ErrorMessage "Failed to build api-gateway image."
Invoke-WithRetry -Command { docker push $apiImage } -ErrorMessage "Failed to push api-gateway image."

Invoke-External -Command { docker build -f services/risk-engine/Dockerfile -t $riskImage . } -ErrorMessage "Failed to build risk-engine image."
Invoke-WithRetry -Command { docker push $riskImage } -ErrorMessage "Failed to push risk-engine image."

Invoke-External -Command { docker build -f services/fl-orchestrator/Dockerfile -t $flImage . } -ErrorMessage "Failed to build fl-orchestrator image."
Invoke-WithRetry -Command { docker push $flImage } -ErrorMessage "Failed to push fl-orchestrator image."

Invoke-External -Command { docker build -f services/alert-service/Dockerfile -t $alertImage . } -ErrorMessage "Failed to build alert-service image."
Invoke-WithRetry -Command { docker push $alertImage } -ErrorMessage "Failed to push alert-service image."

Write-Host "Building and pushing bootstrap web image..."
Invoke-External -Command { docker build -f apps/web/Dockerfile.prod --build-arg VITE_API_BASE="http://localhost:8000" -t $webImageBoot . } -ErrorMessage "Failed to build bootstrap web image."
Invoke-WithRetry -Command { docker push $webImageBoot } -ErrorMessage "Failed to push bootstrap web image."

$tfVarsPath = Join-Path $terraformDir "terraform.auto.tfvars.json"
$tfVars = @{
    region                = $Region
    name_prefix           = $NamePrefix
    postgres_password     = $PostgresPassword
    postgres_user         = "fedrisk"
    postgres_db           = "fedrisk"
    api_gateway_image     = $apiImage
    risk_engine_image     = $riskImage
    fl_orchestrator_image = $flImage
    alert_service_image   = $alertImage
    web_image             = $webImageBoot
}
$tfVars | ConvertTo-Json -Depth 5 | Set-Content -Path $tfVarsPath

Set-Location $terraformDir
Write-Host "Running terraform init..."
Invoke-External -Command { & $terraformPath init -upgrade } -ErrorMessage "Terraform init failed."

Write-Host "Applying infrastructure and backend services..."
Invoke-External -Command { & $terraformPath apply -auto-approve } -ErrorMessage "Terraform apply failed for backend/bootstrap deployment."

Invoke-External -Command { $script:apiUrl = & $terraformPath output -raw api_url } -ErrorMessage "Failed to read api_url from terraform output."
if (-not $apiUrl) {
    throw "Failed to read api_url output from terraform."
}

$webImageFinal = "$registry/$($repositoryMap["web"]):$timestamp-final"
Write-Host "Rebuilding web image with live API base: $apiUrl"
Set-Location $rootDir
Invoke-External -Command { docker build -f apps/web/Dockerfile.prod --build-arg VITE_API_BASE=$apiUrl -t $webImageFinal . } -ErrorMessage "Failed to rebuild web image with live API URL."
Invoke-WithRetry -Command { docker push $webImageFinal } -ErrorMessage "Failed to push final web image."

$tfVars.web_image = $webImageFinal
$tfVars | ConvertTo-Json -Depth 5 | Set-Content -Path $tfVarsPath

Set-Location $terraformDir
Write-Host "Final terraform apply for web service update..."
Invoke-External -Command { & $terraformPath apply -auto-approve } -ErrorMessage "Terraform apply failed for final web rollout."

Invoke-External -Command { $script:webUrl = & $terraformPath output -raw web_url } -ErrorMessage "Failed to read web_url from terraform output."
Invoke-External -Command { $script:apiUrl = & $terraformPath output -raw api_url } -ErrorMessage "Failed to read api_url from terraform output."

Write-Host ""
Write-Host "Deployment complete."
Write-Host "Web URL: $webUrl"
Write-Host "API URL: $apiUrl"
