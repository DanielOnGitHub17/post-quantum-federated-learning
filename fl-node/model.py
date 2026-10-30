"""
ML model that best suits the dataset.
After generation, it will be signed by kyber and transfered to central server
"""

import yfinance as yf
import numpy as np
import pickle
import logging
import time
from pathlib import Path
from tensorflow.keras import Sequential  # type: ignore[reportMissingModuleSource]
from tensorflow.keras.layers import Dense, LSTM  # type: ignore[reportMissingModuleSource]

logger = logging.getLogger(__name__)

PERIOD = "5y"
INTERVAL = "1d"
WINDOW_SIZE = 60
FORECAST_DAYS = 3
EPOCHS = 20
MODEL_DIRECTORY = Path(__file__).parent / "models"
COMPANY_NAMES = {
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet Class A",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
}


def _get_close_data(company):
    logger.info(
        "Fetching close-price data for company=%s (period=%s, interval=%s)",
        company,
        PERIOD,
        INTERVAL,
    )
    start_time = time.perf_counter()
    data = yf.download(company, period=PERIOD, interval=INTERVAL)
    logger.info(
        "Fetching data for %s took %.3f seconds",
        company,
        time.perf_counter() - start_time,
    )
    if data is None or data.empty:
        logger.error("No close-price data returned for company=%s", company)
        raise ValueError(f"No data found for company: {company}")
    close_data = data[["Close"]].reset_index()
    close_data.columns = ["date", "close"]
    logger.info("Loaded %d close-price rows for company=%s", len(close_data), company)
    return close_data


def train_lstm(company):
    logger.info("Preparing model for company=%s", company)
    if not isinstance(company, str) or company.upper() not in COMPANY_NAMES:
        logger.warning("Unsupported company requested: %s", company)
        raise ValueError(f"Unsupported company: {company}")
    company = company.upper()

    model_path = MODEL_DIRECTORY / f"{company.upper()}_lstm.pkl"
    if model_path.exists():
        logger.info("Using cached model for company=%s from %s", company, model_path)
        return model_path.read_bytes()

    close_data = _get_close_data(company)
    prices = close_data["close"].to_numpy(dtype=np.float32)

    if len(prices) < WINDOW_SIZE + FORECAST_DAYS:
        logger.error(
            "Insufficient price history for company=%s: %d rows available, %d required",
            company,
            len(prices),
            WINDOW_SIZE + FORECAST_DAYS,
        )
        raise ValueError(
            f"At least {WINDOW_SIZE + FORECAST_DAYS} closing prices are required"
        )

    minimum = prices.min()
    maximum = prices.max()
    if maximum == minimum:
        logger.error("Price history for company=%s has no variation", company)
        raise ValueError("Closing prices must not all have the same value")

    scaled_prices = (prices - minimum) / (maximum - minimum)
    inputs = []
    targets = []
    for start in range(len(scaled_prices) - WINDOW_SIZE - FORECAST_DAYS + 1):
        end = start + WINDOW_SIZE
        inputs.append(scaled_prices[start:end])
        targets.append(prices[end : end + FORECAST_DAYS])
    logger.info(
        "Prepared %d training samples for company=%s using window=%d",
        len(inputs),
        company,
        WINDOW_SIZE,
    )

    initialization_start_time = time.perf_counter()
    model = Sequential(
        [
            LSTM(64, input_shape=(WINDOW_SIZE, 1)),
            Dense(FORECAST_DAYS),
        ]
    )
    model.compile(optimizer="adam", loss="mean_squared_error")
    logger.info(
        "Initializing the model took %.3f seconds",
        time.perf_counter() - initialization_start_time,
    )

    training_start_time = time.perf_counter()
    model.fit(
        np.asarray(inputs)[..., np.newaxis],
        np.asarray(targets),
        epochs=EPOCHS,
        batch_size=32,
        verbose=0,
    )
    logger.info(
        "Training the model took %.3f seconds",
        time.perf_counter() - training_start_time,
    )
    MODEL_DIRECTORY.mkdir(exist_ok=True)
    model_bytes = pickle.dumps(model)
    model_path.write_bytes(model_bytes)
    logger.info(
        "Saved trained model for company=%s to %s (%d bytes)",
        company,
        model_path,
        len(model_bytes),
    )
    return model_bytes


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    company = "MSFT"
    model = pickle.loads(train_lstm(company))
    close_data = _get_close_data(company)
    prices = close_data["close"].to_numpy(dtype=np.float32)
    minimum = prices.min()
    maximum = prices.max()
    latest_window = ((prices[-WINDOW_SIZE:] - minimum) / (maximum - minimum))[
        np.newaxis, :, np.newaxis
    ]
    predictions = model.predict(latest_window, verbose=0)[0]

    print(f"Predicted next {FORECAST_DAYS} closing prices for {company}:")
    for day, price in enumerate(predictions, start=1):
        print(f"Day {day}: {price:.2f}")
