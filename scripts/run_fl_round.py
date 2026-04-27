from ml.federated.simulation import run_federated_simulation


def main() -> None:
    result = run_federated_simulation(
        num_clients=3,
        num_rounds=2,
        local_epochs=1,
        model_dir="artifacts/models",
    )
    print(result)


if __name__ == "__main__":
    main()
