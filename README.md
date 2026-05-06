# RiskSentinel

a python tool that pulls historical price data, runs a few technical indicators
and tells you whether an asset looks like a buy, hold, sell or a crash warning.
built to be simple to run and easy to extend.


## what it does

it fetches daily ohlcv data from yahoo finance, computes rsi, two moving averages
and a rolling z score, then spits out a signal for each asset you give it.
a death cross between the 50 and 200 day sma combined with a z score below
negative two triggers the crash warning. everything prints straight to the terminal.


## how to use it

clone the repo and install dependencies:

```bash
pip install -r requirements.txt
```

then just run:

```bash
python main.py
```

to change which assets get analyzed, open `main.py` and edit the tickers list at the top:

```python
TICKERS = ["AAPL", "MSFT", "^GSPC", "GLD", "BTC-USD"]
```

you can also adjust the period and sma windows there if you want a different lookback.



## signals

| signal        | when it fires                                          |
|---------------|--------------------------------------------------------|
| crash warning | z score below 2.0 and a death cross is active          |
| sell          | rsi overbought or negative slope with bearish smas     |
| buy           | rsi oversold and sma 50 is above sma 200               |
| hold          | nothing notable going on                               |

---

## disclaimer

this is not financial advice. the signals are mechanical and backward looking.
do not make investment decisions based on this tool alone.
