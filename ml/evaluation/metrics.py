def summarize_metrics(loss: float, accuracy: float) -> dict[str, float]:
    return {"loss": round(loss, 5), "accuracy": round(accuracy, 5)}
