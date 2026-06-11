# LIT Timing Indicator

A Python tool that prepares 1-hour OHLCV data for LIT (Leave In Trade) strategy analysis by automatically converting Iran Standard Time (UTC+3:30) to UTC and labeling each candle with its corresponding trading session.

## What is LIT?

LIT is a price action trading strategy (similar to RTM) that relies heavily on session timing — knowing exactly when London, New York, and Asia sessions open and close is critical for identifying valid setups. This tool is the data preparation layer for applying LIT on historical data.

## What this tool does

- Takes raw 1H OHLCV CSV files exported in **Iran timezone (UTC+3:30)**
- Handles **daylight saving time correctly** — UK DST and US DST are calculated independently, so session boundaries shift accurately twice a year
- Labels each candle with one of four session markers:

| Label | Session | Winter UTC | Summer UTC |
|---|---|---|---|
| `london_open` | London open | 08:00 | 07:00 |
| `ny_open` | New York open | 13:00 | 12:00 |
| `asia_open` | Asia open | 22:00 | 21:00 |
| `asia_close` | Asia close | 06:00 | 05:00 |

Candles that don't fall on a session open/close get `None` — keeping your dataset clean for filtering.

## Supported pairs

`EURUSD` · `AUDUSD` · `GBPUSD` · `XAUUSD` · `EURGBP` · `NAS100` · `NZDUSD` · `US30` · `USDCAD` · `USDCHF` · `USDJPY` · `XAGUSD`

## Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare your data

Place your CSV files in a `data/` folder. Each file should be named as:

```
EUR_USD-60.csv
XAU_USD-60.csv
```

Expected CSV format (no header row):

```
date, time, open, high, low, close, volume
2024.01.02, 09:00, 1.09512, 1.09634, 1.09489, 1.09601, 0
```

### 3. Run

```bash
python 1.LIT_timing.py
```

### 4. Output

Each pair produces a new labeled file in `data/`:

```
data/EURUSD_with_timing.csv
```

With an added `session` column:

```
datetime_utc, datetime_iran, open, high, low, close, session
2024-01-02 08:00:00+00:00, 2024-01-02 11:30:00+03:30, 1.09512, 1.09634, 1.09489, 1.09601, london_open
```

## Why timezone handling matters

Most session scripts hardcode UTC offsets and silently produce wrong labels twice a year. This tool calculates UK and US DST transition dates at runtime for any year in your dataset, so your historical labels are always accurate regardless of the date range.

## Preview

Open `session_times.html` in any browser for an interactive visualization of session open and close times across timezones.

## Tech stack

- Python 3.9+
- pandas
- zoneinfo (built-in, Python 3.9+)

## License

MIT
