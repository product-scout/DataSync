# src/fetcher.py (updated with os.makedirs for logs at top)
import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from tvDatafeed import TvDatafeed, Interval

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_fetcher.log'),
        logging.StreamHandler()
    ]
)

class DataFetcher:
    def __init__(self, csv_path='data/doge_data.csv', symbol='DOGEUSDT.P', exchange='BYBIT', interval=Interval.in_15_minute):
        self.csv_path = csv_path
        self.symbol = symbol
        self.exchange = exchange
        self.interval = interval
        self.tv = TvDatafeed()
        self.interval_minutes = self._get_interval_minutes()
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

    def _get_interval_minutes(self):
        if self.interval == Interval.in_15_minute:
            return 15
        raise ValueError("Unsupported interval")

    def get_historical_data(self, n_bars=10000):
        try:
            data = self.tv.get_hist(
                symbol=self.symbol,
                exchange=self.exchange,
                interval=self.interval,
                n_bars=n_bars
            )
            if data is None or data.empty:
                raise ValueError("No data fetched")
            return data
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def prepare_data(self, df):
        if df is None:
            return None
        df = df.reset_index().rename(columns={'datetime': 'ds', 'close': 'y'})
        return df[['ds', 'y']]

    def load_existing_data(self):
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path, parse_dates=['ds'])
            if not df.empty:
                return df
        return pd.DataFrame(columns=['ds', 'y'])

    def get_last_timestamp(self, df):
        if not df.empty:
            return df['ds'].max()
        return None

    def fetch_new_data(self, last_ts=None, extra_bars=5):
        if last_ts is None:
            raw_data = self.get_historical_data(n_bars=10000)
        else:
            now = datetime.now()
            time_delta = now - last_ts
            bars_needed = int(time_delta.total_seconds() / (self.interval_minutes * 60)) + extra_bars
            bars_needed = max(bars_needed, 1)
            raw_data = self.get_historical_data(n_bars=bars_needed)

        prepared = self.prepare_data(raw_data)
        if prepared is None or prepared.empty:
            return pd.DataFrame(columns=['ds', 'y'])

        if last_ts is not None:
            prepared = prepared[prepared['ds'] > last_ts]

        prepared = prepared.drop_duplicates(subset=['ds']).sort_values('ds')
        return prepared

    def append_to_csv(self, new_data):
        if new_data.empty:
            return
        new_data.to_csv(self.csv_path, mode='a', header=not os.path.exists(self.csv_path), index=False)
        logging.info(f"Appended {len(new_data)} new rows to {self.csv_path}")

    def initial_sync(self):
        existing = self.load_existing_data()
        last_ts = self.get_last_timestamp(existing)
        new_data = self.fetch_new_data(last_ts)
        self.append_to_csv(new_data)
        return self.get_last_timestamp(self.load_existing_data())