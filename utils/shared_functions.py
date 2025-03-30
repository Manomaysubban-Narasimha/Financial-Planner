import datetime
import pandas_market_calendars as mcal
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def is_market_open(date):
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=date, end_date=date)
    return not schedule.empty


def get_previous_market_day(date):
    while not is_market_open(date):
        date = date - timedelta(days=1)
    return date
