from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()

doge_data = tv.get_hist(symbol='DOGEUSDT.P',exchange='BYBIT',interval=Interval.in_15_minute,n_bars=10000)

print(doge_data)
