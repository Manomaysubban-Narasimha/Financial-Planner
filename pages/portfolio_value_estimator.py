import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_market_calendars as mcal
import numpy_financial as npf
import datetime
from utils.shared_functions import is_market_open, get_previous_market_day
from dateutil.relativedelta import relativedelta

# Constants
NUM_OF_MARKET_DAYS_IN_A_YEAR = 252
NUM_OF_MONTHS_IN_A_YEAR = 12


# Function to calculate annualized IRR
def calculate_annualized_irr(daily_investment_amount, closing_prices, portfolio_value):
    cash_flows = [-daily_investment_amount] * len(closing_prices)
    cash_flows.append(portfolio_value)
    irr = npf.irr(cash_flows)
    annual_irr = ((1 + irr) ** NUM_OF_MARKET_DAYS_IN_A_YEAR) - 1
    return annual_irr * 100


def main():
    st.title("Portfolio Value Estimator")

    ticker_symbol = st.text_input("Please enter the ticker symbol of the stock:")

    # Only proceed if ticker_symbol is provided
    if ticker_symbol:
        stock_info = yf.Ticker(ticker_symbol)
        try:
            company_name = stock_info.info['shortName']
        except KeyError:
            st.error("Invalid ticker symbol or no data available.")
            st.stop()

        default_start_date = datetime.date.today() - relativedelta(years=5)
        start_date = st.date_input("Select the start date:", value=default_start_date)
        end_date = st.date_input("Select the end date:", value=datetime.date.today())

        # Input for investment frequency
        frequency = st.selectbox(
            "Are you planning to invest daily, monthly, or yearly?",
            ["Daily", "Monthly", "Yearly"]
        )

        # Input for investment amount based on frequency
        if frequency == "Daily":
            daily_investment_amount = st.number_input(
                "Please enter the amount you are planning to invest daily: $",
                min_value=1.00,
                step=0.50
            )
        elif frequency == "Monthly":
            monthly_investment_amount = st.number_input(
                "Please enter the amount you are planning to invest monthly: $",
                min_value=1.00,
                step=10.0
            )
            daily_investment_amount = (monthly_investment_amount * NUM_OF_MONTHS_IN_A_YEAR) / NUM_OF_MARKET_DAYS_IN_A_YEAR
        elif frequency == "Yearly":
            yearly_investment_amount = st.number_input(
                "Please enter the amount you are planning to invest yearly: $",
                min_value=10.0,
                step=100.0
            )
            daily_investment_amount = yearly_investment_amount / NUM_OF_MARKET_DAYS_IN_A_YEAR

        # Add Calculate button
        if st.button("Calculate Portfolio Value"):
            # Adjust start_date to the previous market day if necessary
            adjusted_start_date = get_previous_market_day(start_date)
            if adjusted_start_date != start_date:
                st.write(f"Note: Start date adjusted to the previous market day: {adjusted_start_date}")

            # Define today's date and ten days prior
            today_date = datetime.date.today()
            ten_days_before_today = today_date - datetime.timedelta(days=10)

            # Fetch stock data
            stock_data = yf.download(ticker_symbol, start=adjusted_start_date, end=end_date)
            past_ten_days_stock_data = yf.download(ticker_symbol, start=ten_days_before_today, end=today_date)

            # Check if data is available
            if stock_data.empty or past_ten_days_stock_data.empty:
                st.error("No stock data available for the specified period.")
                st.stop()

            # Extract closing prices
            closing_prices = stock_data['Close'].values.flatten().tolist()
            past_ten_days_closing_prices = past_ten_days_stock_data['Close'].values.flatten().tolist()

            # Calculate financial metrics
            average_price = sum(closing_prices) / len(closing_prices)
            latest_closing_price = closing_prices[-1]
            todays_closing_price = past_ten_days_closing_prices[-1]

            num_investment_days = len(closing_prices)
            invested_amount = daily_investment_amount * num_investment_days
            rate_of_return = ((latest_closing_price / average_price) - 1) * 100
            profit = invested_amount * (rate_of_return / 100)
            portfolio_value = invested_amount + profit
            num_of_stocks = portfolio_value / latest_closing_price
            todays_portfolio_value = num_of_stocks * todays_closing_price

            final_today_rate_of_return = ((todays_portfolio_value / invested_amount) - 1)
            final_today_rate_of_return_percent = final_today_rate_of_return * 100
            final_profit = round(invested_amount * final_today_rate_of_return, 2)

            annual_irr_percent = calculate_annualized_irr(daily_investment_amount, closing_prices, todays_portfolio_value)

            # Display results in a green box with black text
            st.markdown(
                f"""
                <div style="background-color: #d4edda; padding: 20px; border-radius: 5px; color: black;">
                    <h3>Results</h3>
                    <p>Average price of {ticker_symbol} during the time period: <strong>${average_price:.2f}</strong></p>
                    <p>Price of {ticker_symbol} at the end of the time period: <strong>${latest_closing_price:.2f}</strong></p>
                    <p>Absolute Rate of return upon {frequency.lower()} Dollar Cost Averaging for {company_name} 
                    from {adjusted_start_date} to {end_date}: <strong>{rate_of_return:,.2f}%</strong></p>
                    <p>Amount invested: <strong>${invested_amount:,.2f}</strong></p>
                    <p>Profit: <strong>${profit:,.2f}</strong></p>
                    <p>Portfolio value: <strong>${portfolio_value:,.2f}</strong></p>
                    <p>Number of stocks: <strong>{num_of_stocks:,.2f}</strong></p>
                    {f"<p>If you had held onto the {company_name} stocks until today, your portfolio value would have been: <strong>${todays_portfolio_value:,.2f}</strong> with a net growth of <strong>${final_profit:,}</strong> which is <strong>{final_today_rate_of_return_percent:,.2f}%</strong> of net growth</p>" if end_date <= today_date else ""}
                    {f"<p>Annualized Internal Rate of Return = <strong>{annual_irr_percent:,.2f}%</strong></p>" if end_date <= today_date else ""}
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()