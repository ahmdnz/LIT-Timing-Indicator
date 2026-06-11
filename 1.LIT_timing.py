import pandas as pd
from zoneinfo import ZoneInfo
import re

tehran = ZoneInfo("Asia/Tehran")
utc    = ZoneInfo("UTC")

def is_uk_dst(dt):
    """Last Sunday of March → last Sunday of October"""
    year = dt.year
    last_sun_march = max(
        pd.Timestamp(year, 3, day, tzinfo=utc)
        for day in range(25, 32)
        if pd.Timestamp(year, 3, day).dayofweek == 6
    )
    last_sun_october = max(
        pd.Timestamp(year, 10, day, tzinfo=utc)
        for day in range(25, 32)
        if pd.Timestamp(year, 10, day).dayofweek == 6
    )
    return last_sun_march <= dt < last_sun_october

def is_us_dst(dt):
    """2nd Sunday of March → 1st Sunday of November"""
    year = dt.year
    sundays_march = [
        pd.Timestamp(year, 3, day, tzinfo=utc)
        for day in range(1, 32)
        if pd.Timestamp(year, 3, day).dayofweek == 6
    ]
    second_sun_march = sundays_march[1]
    sundays_november = [
        pd.Timestamp(year, 11, day, tzinfo=utc)
        for day in range(1, 8)
        if pd.Timestamp(year, 11, day).dayofweek == 6
    ]
    first_sun_november = sundays_november[0]
    return second_sun_march <= dt < first_sun_november

def get_session_opens(dt):
    """
    Returns the 4 session open times (UTC) for a given date.

    London open  = 09:00 Berlin local
      Berlin winter (UTC+1) → 08:00 UTC
      Berlin summer (UTC+2) → 07:00 UTC

    NY open = 08:00 NY local
      NY winter (UTC-5) → 13:00 UTC
      NY summer (UTC-4) → 12:00 UTC

    Asia open  = 17:00 NY local
      NY winter (UTC-5) → 22:00 UTC
      NY summer (UTC-4) → 21:00 UTC

    Asia close = 01:00 NY local (next day)
      NY winter (UTC-5) → 06:00 UTC
      NY summer (UTC-4) → 05:00 UTC
    """
    uk_dst = is_uk_dst(dt)
    us_dst = is_us_dst(dt)

    london_open = 7  if uk_dst else 8
    ny_open     = 12 if us_dst else 13
    asia_open   = 21 if us_dst else 22
    asia_close  = 5  if us_dst else 6

    return london_open, ny_open, asia_open, asia_close

def label_session(row):
    """
    Labels a candle with its session based on datetime_utc.
    Each session open is a single 1-hour candle.
    Asia close is also treated as a single 1-hour candle.
    """
    dt   = row['datetime_utc']
    hour = dt.hour

    london_open, ny_open, asia_open, asia_close = get_session_opens(dt)

    if hour == london_open:
        return 'london_open'
    elif hour == ny_open:
        return 'ny_open'
    elif hour == asia_open:
        return 'asia_open'
    elif hour == asia_close:
        return 'asia_close'
    else:
        return None

def make_data(path):
    data = pd.read_csv(path, names=["date", "time", "open", "high", "low", "close", "volume"])

    # Step 1: Merge date and time columns into a single datetime column
    data['datetime_iran'] = pd.to_datetime(data['date'] + ' ' + data['time'])

    # Step 2: Localize to Iran timezone
    data['datetime_iran'] = data['datetime_iran'].dt.tz_localize(
        tehran,
        ambiguous='infer',
        nonexistent='shift_forward'
    )

    # Step 3: Convert to UTC
    data['datetime_utc'] = data['datetime_iran'].dt.tz_convert(utc)
    data.drop(columns=['date', 'time', 'volume'], inplace=True)
    data = data[['datetime_utc', 'datetime_iran', 'open', 'high', 'low', 'close']]
    # data.set_index('datetime_utc', inplace=True)

    # Apply to dataframe
    data['session'] = data.apply(label_session, axis=1)

    pair = re.search(r'([A-Z0-9]+)_([A-Z]+)', path)
    # print(pair, path)
    f_name = pair.group(1) + pair.group(2)  # 'EURUSD'
    f_name = f"{f_name}_with_timing"
    data.to_csv(f'data/{f_name}.csv', index=False)
    print(f_name, 'successfully maked!')



if __name__ == "__main__":
    symbol_list = ['EUR_USD', 'AUD_USD', 'GBP_USD', 'XAU_USD', 'EUR_GBP',
                   'NAS100_USD', 'NZD_USD', 'US30_USD', 'USD_CAD','USD_CHF',
                   'USD_JPY', 'XAG_USD']
    
    for symbol in symbol_list:
        print('making file for', symbol)
        data_path = f'data/{symbol}-60.csv'
        make_data(data_path)