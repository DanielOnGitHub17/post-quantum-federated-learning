"""Small Tkinter application for three-day stock-price predictions."""

import pickle
import logging
from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

import numpy as np
import keras
import yfinance as yf

COMPANIES = {"NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"}
FORECAST_DAYS = 3
WINDOW_SIZE = 60
MODEL_BUNDLE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "models.pkl"
logger = logging.getLogger(__name__)


def load_models() -> dict[str, Any]:
    if not MODEL_BUNDLE.exists():
        raise FileNotFoundError(f"Model bundle not found: {MODEL_BUNDLE}")
    if not hasattr(keras, "Model"):
        raise RuntimeError("Keras is not available for model deserialization")
    with MODEL_BUNDLE.open("rb") as bundle_file:
        serialized_models = pickle.load(bundle_file)
    if not isinstance(serialized_models, dict):
        raise ValueError("Model bundle must contain a company-to-model map")

    models: dict[str, Any] = {}
    for company, serialized_model in serialized_models.items():
        if not isinstance(company, str) or not isinstance(serialized_model, bytes):
            raise ValueError(
                "Model bundle entries must contain company names and serialized models"
            )
        models[company] = pickle.loads(serialized_model)
    logger.info(
        "Loaded model bundle: path=%s companies=%s",
        MODEL_BUNDLE,
        ", ".join(sorted(models)),
    )
    return models


def predict_next_three_days(model: Any, company: str) -> np.ndarray:
    logger.info("Fetching prediction data: company=%s", company)
    data = yf.download(company, period="3mo", interval="1d", progress=False)
    if data is None or data.empty:
        raise ValueError(f"No market data found for {company}")

    prices = data[["Close"]].to_numpy(dtype=np.float32).reshape(-1)
    if len(prices) < WINDOW_SIZE:
        raise ValueError(f"At least {WINDOW_SIZE} closing prices are required")

    minimum = prices.min()
    maximum = prices.max()
    if maximum == minimum:
        raise ValueError("Closing prices must not all have the same value")

    latest_window = ((prices[-WINDOW_SIZE:] - minimum) / (maximum - minimum))[
        np.newaxis, :, np.newaxis
    ]
    prediction = model.predict(latest_window, verbose=0)[0]
    if len(prediction) != FORECAST_DAYS:
        raise ValueError(f"Model must return exactly {FORECAST_DAYS} predictions")
    predictions = np.asarray(prediction)
    logger.info("Prediction completed: company=%s days=%d", company, len(predictions))
    return predictions


class PredictionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.models = load_models()
        self.company_entry = ttk.Entry(root, width=20)
        self.company_entry.grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(
            root,
            text="Predict next three days",
            command=self.predict,
        ).grid(row=0, column=1, padx=10, pady=10)
        self.result = ttk.Label(root, text="Enter a Nasdaq acronym.")
        self.result.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def predict(self) -> None:
        company = self.company_entry.get().strip().upper()
        if company not in COMPANIES or company not in self.models:
            messagebox.showerror(
                "Prediction error", f"No model is available for {company}."
            )
            return

        try:
            predictions = predict_next_three_days(self.models[company], company)
        except (ValueError, OSError, TypeError) as error:
            messagebox.showerror("Prediction error", str(error))
            return

        formatted = "\n".join(
            f"Day {day}: ${price:.2f}" for day, price in enumerate(predictions, start=1)
        )
        self.result.configure(text=f"{company}\n{formatted}")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Starting stock prediction application")
    root = tk.Tk()
    root.title("Stock prediction")
    PredictionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
