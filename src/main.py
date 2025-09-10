# src/main.py (updated with scheduled fetching and forecasting)
import time
from datetime import datetime, timedelta
from fetcher import DataFetcher
from forecaster import Forecaster

fetcher = DataFetcher()
forecaster = Forecaster()

# Initial sync and forecast
last_ts = fetcher.initial_sync()
forecaster.run_forecast()

def get_next_fetch_time(current_time: datetime) -> datetime:
    minute = current_time.minute
    if minute < 1:
        return current_time.replace(minute=1, second=0, microsecond=0)
    elif minute < 16:
        return current_time.replace(minute=16, second=0, microsecond=0)
    elif minute < 31:
        return current_time.replace(minute=31, second=0, microsecond=0)
    elif minute < 46:
        return current_time.replace(minute=46, second=0, microsecond=0)
    else:
        next_hour = current_time + timedelta(hours=1)
        return next_hour.replace(minute=1, second=0, microsecond=0)

while True:
    now = datetime.now()
    next_time = get_next_fetch_time(now)
    sleep_seconds = (next_time - now).total_seconds()
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    
    # Fetch new data
    new_data = fetcher.fetch_new_data(last_ts)
    if not new_data.empty:
        fetcher.append_to_csv(new_data)
        last_ts = new_data['ds'].max()
    
    # Run forecast after fetch (even if no new data, to refresh)
    forecaster.run_forecast()