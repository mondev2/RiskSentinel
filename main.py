# main
# entry point that orchestrates data fetching, analysis, and report printing

import math
import sys

import data_engine as de
import analysis as an


# configuration

TICKERS       = ["AAPL", "MSFT", "^GSPC", "GLD", "BTC-USD"]
PERIOD        = "2y"
INTERVAL      = "1d"

SMA_FAST_WINDOW = 50
SMA_SLOW_WINDOW = 200
RSI_PERIOD      = 14
ZSCORE_WINDOW   = 252

COLUMN_WIDTH = 72


# formatting helpers

def divider(char: str = "-") -> str:
    return char * COLUMN_WIDTH


def fmt_float(value: float, decimals: int = 2) -> str:
    if math.isnan(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_bool(value: bool) -> str:
    return "YES" if value else "NO"


def signal_badge(signal: str) -> str:
    return f"[ {signal} ]"


# core analysis runner

def run_analysis(ticker: str) -> dict | None:
    """
    Fetch data and compute the full signal for a single ticker.
    Returns a result dict on success, or None if data is unavailable.
    """
    try:
        df = de.fetch_ohlcv(ticker, period=PERIOD, interval=INTERVAL)
    except ValueError as exc:
        print(f"  data error for {ticker}: {exc}")
        return None

    close = de.get_close_series(df)

    # need enough bars to compute the slow sma with room to spare
    min_bars = SMA_SLOW_WINDOW + 10
    if len(close) < min_bars:
        print(f"  skipped {ticker}: insufficient data (need {min_bars} bars, got {len(close)}).")
        return None

    sma50      = an.sma(close, SMA_FAST_WINDOW)
    sma200     = an.sma(close, SMA_SLOW_WINDOW)
    rsi_series = an.rsi(close, RSI_PERIOD)
    zscore     = an.rolling_zscore(close, ZSCORE_WINDOW)

    result = an.generate_signal(close, sma50, sma200, rsi_series, zscore)

    result["ticker"]        = ticker
    result["bars_analyzed"] = len(close)
    result["data_start"]    = str(close.index[0].date())
    result["data_end"]      = str(close.index[-1].date())

    return result


# report printer

def print_report(results: list[dict]) -> None:
    """Render all analysis results as a formatted terminal report."""

    print()
    print(divider("="))
    print("  market analysis report")
    print(f"  period: {PERIOD} | interval: {INTERVAL} | "
          f"sma windows: {SMA_FAST_WINDOW}/{SMA_SLOW_WINDOW} | rsi period: {RSI_PERIOD}")
    print(divider("="))

    for res in results:
        ticker = res["ticker"]
        signal = res["signal"]

        print()
        print(divider())
        print(f"  ticker  : {ticker}")
        print(f"  signal  : {signal_badge(signal)}")
        print(divider())
        print(f"  data range      : {res['data_start']} to {res['data_end']}  ({res['bars_analyzed']} bars)")
        print(f"  latest close    : {fmt_float(res['latest_close'])}")
        print(f"  sma {SMA_FAST_WINDOW}          : {fmt_float(res['latest_sma50'])}")
        print(f"  sma {SMA_SLOW_WINDOW}         : {fmt_float(res['latest_sma200'])}")
        print(f"  rsi ({RSI_PERIOD})        : {fmt_float(res['latest_rsi'], 1)}")
        print(f"  z score         : {fmt_float(res['latest_zscore'], 3)}")
        print(f"  death cross     : {fmt_bool(res['death_cross'])}")
        print(f"  trend slope     : {fmt_float(res['trend_slope'], 5)}")
        print()
        print(f"  reason: {res['reason']}")

    print()
    print(divider("="))
    print("  signal summary")
    print(divider("="))

    max_len = max(len(r["ticker"]) for r in results)
    for res in results:
        padding = " " * (max_len - len(res["ticker"]))
        print(f"  {res['ticker']}{padding}  -->  {signal_badge(res['signal'])}")

    print()
    print(divider("="))
    print("  disclaimer")
    print(divider())
    print("  this output is for informational and educational purposes only.")
    print("  it does not constitute financial advice or investment recommendations.")
    print("  past signals do not guarantee future results.")
    print("  consult a qualified financial professional before making any decisions.")
    print(divider("="))
    print()


# entry point

def main() -> None:
    print()
    print(divider("="))
    print("  initializing market analysis tool")
    print(divider("="))

    results = []
    for ticker in TICKERS:
        print(f"  fetching and analyzing: {ticker} ...")
        result = run_analysis(ticker)
        if result is not None:
            results.append(result)

    if not results:
        print()
        print("  no valid results were produced. exiting.")
        sys.exit(1)

    print_report(results)


if __name__ == "__main__":
    main()