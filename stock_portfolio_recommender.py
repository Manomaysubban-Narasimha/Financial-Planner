import streamlit as st 
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go


def render_ETF(etf):
    st.write(f"Invest in the ETF: {etf}")
            
    timeframes = st.selectbox(
        "Select Timeframe",
        ["1D", "1W", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
    )
    
    chart_type = st.radio(
        "Select Chart Type",
        ["Line", "Candlestick"]
    )
    
    etf_data = yf.Ticker(etf)
    
    end_date = datetime.now()
    if timeframes == "1D":
        start_date = end_date - timedelta(days=1)
        interval = "1m"
    elif timeframes == "1W":
        start_date = end_date - timedelta(weeks=1)
        interval = "1h"
    elif timeframes == "1M":
        start_date = end_date - timedelta(days=30)
        interval = "1d"
    elif timeframes == "6M":
        start_date = end_date - timedelta(days=180)
        interval = "1d"
    elif timeframes == "YTD":
        start_date = datetime(end_date.year, 1, 1)
        interval = "1d"
    elif timeframes == "1Y":
        start_date = end_date - timedelta(days=365)
        interval = "1d"
    elif timeframes == "5Y":
        start_date = end_date - timedelta(days=1825)
        interval = "1d"
    else:  # MAX
        start_date = None
        interval = "1d"
    
    historical_data = etf_data.history(start=start_date, end=end_date, interval=interval)
    
    st.dataframe(historical_data)
    
    
    if chart_type == "Line":
        st.line_chart(historical_data['Close'])
    else:  # Candlestick
        fig = go.Figure(data=[go.Candlestick(x=historical_data.index,
            open=historical_data['Open'],
            high=historical_data['High'],
            low=historical_data['Low'],
            close=historical_data['Close'])])
        
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


def main():
    st.title("Stock Recommender")
    risk_level = st.slider(
        "Select Your Risk Tolerance",
        min_value=1,
        max_value=5,
        value=3,
        help="1 = Very Low Risk, 2 = Low Risk, 3 = Medium Risk, 4 = High Risk, 5 = Very High Risk"
    )
    
    match risk_level:
        case 1:
            render_ETF("VOO")
        case 2:
            render_ETF("QQQM")
        case 3:
            st.write("In progress: Perform fundamental analysis and sentiment analysis on Large Cap Companies, then recommend 5-10 top picks")
        case 4:
            st.write("Perform fundamental analysis and sentiment analysis on Mid Cap Companies, then recommend 5-10 top picks")
        case 5:
            st.write("Perform fundamental analysis and sentiment analysis on Small Cap Companies, then recommend 5-10 top picks")


if __name__ == "__main__":
    main()
    