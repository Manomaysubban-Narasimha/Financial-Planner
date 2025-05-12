import requests
import json
import certifi
import tqdm
import streamlit as st 
import pandas as pd
from datetime import datetime, timedelta
from urllib.request import urlopen
import plotly.graph_objects as go

from pages.stock_analyzer import get_average_recommendation_rating
from pages.stock_analyzer import format_value


MEGA_CAP_THRESHOLD = 200e9   # $200 billion or more
LARGE_CAP_THRESHOLD = 10e9   # $10 billion or more (but less than mega cap)
MID_CAP_THRESHOLD = 2e9      # $2 billion or more (but less than large cap)

SUCCESSFUL_REQUEST = 200


def render_ETF(etf):
    st.write(f"<b>Recommendation:</b> Invest in the <b>{etf}</b> ETF", unsafe_allow_html=True)
            
    timeframes = st.selectbox(
        "Select Timeframe",
        ["1D", "1W", "1M", "6M", "YTD", "1Y", "5Y", "MAX"],
        index=5  # Index 5 corresponds to "1Y"
    )
    
    chart_type = st.radio(
        "Select Chart Type",
        ["Line", "Candlestick"]
    )
    
    end_date = datetime.now()
    if timeframes == "1D":
        start_date = end_date - timedelta(days=1)
        interval = "1min"
    elif timeframes == "1W":
        start_date = end_date - timedelta(weeks=1)
        interval = "1hour" 
    elif timeframes == "1M":
        start_date = end_date - timedelta(days=30)
        interval = "1day"
    elif timeframes == "6M":
        start_date = end_date - timedelta(days=180)
        interval = "1day"
    elif timeframes == "YTD":
        start_date = datetime(end_date.year, 1, 1)
        interval = "1day"
    elif timeframes == "1Y":
        start_date = end_date - timedelta(days=365)
        interval = "1day"
    elif timeframes == "5Y":
        start_date = end_date - timedelta(days=1825)
        interval = "1day"
    else:  # MAX
        start_date = None
        interval = "1day"

    api_key = st.secrets["fmp_api_key"]
    
    if start_date:
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/{interval}/{etf}?from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&apikey={api_key}"
    else:
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/{interval}/{etf}?apikey={api_key}"
        
    response = requests.get(url)
    if response.status_code == SUCCESSFUL_REQUEST:
        data = response.json()
        historical_data = pd.DataFrame(data)
        historical_data['date'] = pd.to_datetime(historical_data['date'])
        historical_data.set_index('date', inplace=True)
        historical_data.sort_index(inplace=True)
        
        if chart_type == "Line":
            st.line_chart(historical_data['close'])
        else:  # Candlestick
            fig = go.Figure(data=[go.Candlestick(x=historical_data.index,
                open=historical_data['open'],
                high=historical_data['high'],
                low=historical_data['low'],
                close=historical_data['close'])])
            
            # to avoid displaying weekends and non-market days
            fig.update_layout(
                xaxis={
                    'type': 'category',
                    'title': 'Date'
                },
                yaxis={'title': 'Price'},
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig)


def get_constituents(min_market_cap, max_market_cap):
    api_key = st.secrets["fmp_api_key"]
    url = f"https://financialmodelingprep.com/stable/company-screener?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == SUCCESSFUL_REQUEST:
        data = response.json()
        print(f"\n\n\ndata retrieved: {data}\n\n\n")
        print(f"\n\n\nType of data retrieved: {type(data)}\n\n\n")
        filtered_data = [company for company in data if min_market_cap < company.get('marketCap', 0) <= max_market_cap]
        
        # Create a table with company data sorted by market cap
        st.write("### Companies")
        company_table = []
        for company in sorted(filtered_data, key=lambda x: x.get('marketCap', 0), reverse=True):
            company_table.append({
                "Symbol": company.get('symbol', ''),
                "Name": company.get('companyName', ''),
                "Market Cap": format_value(company.get('marketCap', 0))
            })
        
        st.table(company_table)
        symbols = [company['Symbol'] for company in company_table]
        st.write("### Selected Symbols")
        st.write(f"{len(symbols)} symbols")
        st.write(f"Type of symbols = {type(symbols)} of {type(symbols[0])}")
        st.write(symbols)
        return symbols
        
    else:
        print("ERROR in Retrieving Data: get_constituents(min_market_cap, max_market_cap)")


def is_stock(symbol):
    try:
        fmp_api_key = st.secrets["fmp_api_key"]
        url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={fmp_api_key}"
        response = requests.get(url)
        
        if response.status_code == SUCCESSFUL_REQUEST:
            data = response.json()

            print(f"\n\n\nin_stock(symbol) data = {data};\n type of data = {type(data)}\n\n\n")

            is_etf = data[0]["isEtf"]
            is_fund = data[0]["isFund"]
            is_actively_trading = data[0]["isActivelyTrading"]
            if is_actively_trading:
                if is_etf or is_fund:
                    return False
                return True
            else:
                return False  # ignore stocks that are not actively trading
            
    except Exception as e:
        print(f"Error checking if {symbol} is a stock: {e}")
        return False


def main():
    st.title("Stock Recommender")
    risk_level = st.slider(
        "Select Your Risk Tolerance",
        min_value=1,
        max_value=5,
        value=1,
        help="1 = Very Low Risk, 2 = Low Risk, 3 = Medium Risk, 4 = High Risk, 5 = Very High Risk"
    )
    
    match risk_level:
        case 1:
            render_ETF("VOO")
        case 2:
            render_ETF("QQQM")
        case 3:
            st.write("**In progress**: Perform fundamental analysis and sentiment analysis on Large Cap Companies, then recommend 5-10 top picks")
            recommend_mega_cap()
        case 4:
            st.write("**In progress**: Perform fundamental analysis and sentiment analysis on Mid Cap Companies, then recommend 5-10 top picks")
        case 5:
            st.write("**In progress**: Perform fundamental analysis and sentiment analysis on Small Cap Companies, then recommend 5-10 top picks")


if __name__ == "__main__":
    main()