import datetime
import pandas_market_calendars as mcal

def is_market_open(date):
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=date, end_date=date)
    return not schedule.empty


def get_previous_market_day(date):
    while not is_market_open(date):
        date = date - datetime.timedelta(days=1)
    return date
