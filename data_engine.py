# data engine
# handles all yfinance api calls and returns clean analysis ready dataframes

import yfinance as yf
import pandas as pd


def fetch_ohlcv(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """
    Download OHLCV data for a given ticker symbol.

    Parameters
    ----------
    ticker   : str  - A valid ticker symbol, e.g. 'AAPL' or '^GSPC'.
    period   : str  - Lookback window accepted by yfinance, e.g. '1y', '2y', '5y'.
    interval : str  - Bar size accepted by yfinance, e.g. '1d', '1wk'.

    Returns
    -------
    pd.DataFrame with columns: Open, High, Low, Close, Volume.
                 Index is a timezone-naive DatetimeIndex.

    Raises
    ------
    ValueError if the download returns an empty DataFrame or lacks a 'Close' column.
    """
    raw = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)

    if raw.empty:
        raise ValueError(
            f"No data returned for ticker '{ticker}'. "
            "Verify the symbol and your network connection."
        )

    # flatten multiindex columns produced by yfinance 0.2 and above
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    required_columns = {"Open", "High", "Low", "Close", "Volume"}
    missing = required_columns - set(raw.columns)
    if missing:
        raise ValueError(f"Downloaded data for '{ticker}' is missing columns: {missing}")

    # drop rows where close is nan to remove weekend bleed through and halted days
    cleaned = raw.dropna(subset=["Close"]).copy()

    # ensure the index is timezone naive for consistent downstream arithmetic
    if cleaned.index.tz is not None:
        cleaned.index = cleaned.index.tz_localize(None)

    cleaned.sort_index(inplace=True)
    return cleaned


def get_close_series(df: pd.DataFrame) -> pd.Series:
    """
    Extract and validate the Close price series from an OHLCV DataFrame.

    Parameters
    ----------
    df : pd.DataFrame - Output of fetch_ohlcv().

    Returns
    -------
    pd.Series of closing prices with a DatetimeIndex.
    """
    if "Close" not in df.columns:
        raise KeyError("DataFrame does not contain a 'Close' column.")
    return df["Close"].dropna()