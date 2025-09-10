# DataSync

A worker script to fetch and sync DOGEUSDT.P 15-minute data from Bybit to a CSV file, suitable for Prophet forecasting.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
3. Install deps: `pip install -r requirements.txt`
4. Run: `python src/main.py`

## Future Extensions
- Add a `forecaster.py` in src/ that loads `data/doge_data.csv`, runs Prophet, and saves forecasts to `data/doge_forecast.csv`.
- Example: Import Prophet, fit on df[['ds', 'y']], forecast, append to forecast CSV.
- Run it periodically or after data updates.

## Save Requierments
pip freeze > requirements.txt