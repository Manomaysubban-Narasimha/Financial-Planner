import requests
import json
import certifi
import tqdm
import streamlit as st 
import pandas as pd
from datetime import datetime, timedelta
from urllib.request import urlopen
import plotly.graph_objects as go

import pages.stock_analyzer
from pages.stock_analyzer import get_average_recommendation_rating
from pages.stock_analyzer import format_value


ONE_DAY = 24*3600

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


def recommend_from_nasdaq100():
    @st.cache_data(ttl=ONE_DAY) 
    def fetch_nasdaq100_data(api_key):
        url = f"https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey={api_key}"
        response = requests.get(url)
        return response.json()

    @st.cache_data(ttl=ONE_DAY) 
    def get_ratings_and_net_incomes(api_key, symbols):
        symbol_rating = {}
        net_incomes = {}
        
        for symbol in symbols:
            if symbol == "GOOG":  # Skip GOOG in favor of GOOGL since GOOGL provides voting rights for shareholders
                continue
            symbol_rating[symbol] = get_average_recommendation_rating(symbol)
            
            url = f"https://financialmodelingprep.com/stable/income-statement?symbol={symbol}&apikey={api_key}"
            response = requests.get(url)
            if response.status_code == SUCCESSFUL_REQUEST:
                data = response.json()
                if data:
                    net_incomes[symbol] = data[0]['netIncome']
                    
        return symbol_rating, net_incomes

    api_key = st.secrets["fmp_api_key"]
    
    constituents = fetch_nasdaq100_data(api_key)
    
    # Create a mapping of symbols to company names
    symbol_to_name = {constituent['symbol']: constituent['name'] for constituent in constituents}
    symbols = list(symbol_to_name.keys())
    
    symbol_rating, net_incomes = get_ratings_and_net_incomes(api_key, symbols)
    
    # Sort by rating first, then by net income for ties, and get top 10
    sorted_symbol_rating = dict(list(sorted(symbol_rating.items(),
        key=lambda x: (x[1], net_incomes.get(x[0], 0)),
        reverse=True))[:10])
    
    st.write("### Top 10 Recommendations")
    
    # Create a DataFrame for better display
    recommendations_data = []
    for symbol, rating in sorted_symbol_rating.items():
        recommendations_data.append({
            "Symbol": symbol,
            "Company Name": symbol_to_name[symbol],
            "Rating": round(rating, 5),
            # "Net Income": f"${net_incomes[symbol]:,.2f}"
        })
    
    df = pd.DataFrame(recommendations_data)
    st.dataframe(df, hide_index=True)


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

    score_map = {
        "1-3 years": 1,
        "3-7 years": 2,
        "7+ years": 3,
        "Up to 10% CAGR": 1,
        "10-14% CAGR": 2,
        "Greater than 14% CAGR": 3,
        "Low": 1,
        "Medium": 2,
        "High": 3,

    }

    investment_horizon = st.radio(
        "What is your investment time horizon?",
        ["1-3 years", "3-7 years", "7+ years"],
        help="How long do you plan to keep your money invested?"
    )

    desired_roi = st.radio(
        "What is your desired annual return on investment?",
        ["Up to 10% CAGR", "10-14% CAGR", "Greater than 14% CAGR"],
        help="What annual percentage return are you aiming to achieve with your investments?"
    )
    risk_tolerance = st.select_slider(
        "Select Your Risk Tolerance",
        options=["Low", "Medium", "High"],
        value="Low",
        help="Choose your preferred level of investment risk tolerance"
    )

    score = round((score_map[investment_horizon] + score_map[desired_roi] + score_map[risk_tolerance]) / 3)
    
    match score:
        case 1:
            render_ETF("VOO")
        case 2:
            render_ETF("QQQM")
        case 3:
            recommend_from_nasdaq100()


if __name__ == "__main__":
    main()