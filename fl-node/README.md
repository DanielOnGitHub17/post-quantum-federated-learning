# LSTM Stock Prediction

`model.py` trains an LSTM model using a company's daily closing prices and
predicts the next three closing prices.

## Requirements

Install the Python dependencies:

```powershell
pip install numpy tensorflow yfinance
```

## Predict from the command line

From the `fl-node` directory, run:

```powershell
python model.py
```

The script downloads five years of daily data for `MSFT`, trains the model,
and prints three predicted closing prices:

```text
Predicted next 3 closing prices for MSFT:
Day 1: ...
Day 2: ...
Day 3: ...
```

To predict another company, change the `company` value in the
`if __name__ == "__main__":` block:

```python
company = "AAPL"
```

Use the ticker symbol supported by Yahoo Finance.

## Use from Python

Import `train_lstm` and pass it a company ticker:

```python
from model import train_lstm

model = train_lstm("MSFT")
```

`train_lstm` returns the trained Keras model. The model expects an input
containing the most recent 60 daily closing prices, shaped as:

```text
(1, 60, 1)
```

Its output contains three predicted closing prices:

```python
predictions = model.predict(latest_window)
```

The current executable example in `model.py` downloads and prepares the
latest input window before calling `predict`.

## Model caching

The first training run saves the model as
`models/<TICKER>_lstm.pkl`. For example, the MSFT model is saved as
`models/MSFT_lstm.pkl`.

When `train_lstm` is called again for the same ticker, it loads that pickle
instead of downloading data and retraining. Delete the ticker's pickle file
when a fresh model is needed.

## How the prediction works

1. Download five years of daily market data with `yfinance`.
2. Keep the `Close` column.
3. Normalize the closing prices.
4. Build training samples from windows of 60 trading days.
5. Train an LSTM with a dense output layer containing three values.
6. Use the latest 60 closing prices to predict the next three prices.

The predictions are estimates and should not be treated as financial advice.
