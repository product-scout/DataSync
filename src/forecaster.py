# src/forecaster.py
import os
import logging
import pandas as pd
from prophet import Prophet

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/forecaster.log'),
        logging.StreamHandler()
    ]
)

class Forecaster:
    def __init__(self, historical_csv='data/doge_data.csv', forecast_csv='data/doge_forecast.csv', periods=30):
        self.historical_csv = historical_csv
        self.forecast_csv = forecast_csv
        self.periods = periods
        os.makedirs(os.path.dirname(self.forecast_csv), exist_ok=True)

    def run_forecast(self):
        try:
            df = pd.read_csv(self.historical_csv, parse_dates=['ds'])
            if df.empty:
                logging.warning("No historical data for forecasting.")
                return

            model = Prophet()
            model.fit(df)

            # Include historical and future periods
            future = model.make_future_dataframe(periods=self.periods, freq='15min', include_history=True)
            forecast = model.predict(future)
            # Rename columns for clarity
            forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(
                columns={
                    'yhat': 'predicted',
                    'yhat_lower': 'lower_bound',
                    'yhat_upper': 'upper_bound'
                }
            )

            # Load existing forecast, keep historical part, override future
            last_hist_ds = df['ds'].max()
            if os.path.exists(self.forecast_csv):
                existing_forecast = pd.read_csv(self.forecast_csv, parse_dates=['ds'])
                # Keep only existing forecast rows up to last historical timestamp
                existing_forecast = existing_forecast[existing_forecast['ds'] <= last_hist_ds]
            else:
                existing_forecast = pd.DataFrame(columns=['ds', 'predicted', 'lower_bound', 'upper_bound'])

            # Combine existing (historical) with new forecast (historical + future)
            updated_forecast = pd.concat([existing_forecast, forecast]).drop_duplicates(subset=['ds']).sort_values('ds')
            updated_forecast.to_csv(self.forecast_csv, index=False)
            logging.info(f"Updated forecast with {len(forecast)} periods (including historical) and saved to {self.forecast_csv}")
        except Exception as e:
            logging.error(f"Error in forecasting: {e}")