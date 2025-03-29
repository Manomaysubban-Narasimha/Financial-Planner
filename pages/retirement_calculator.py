import streamlit as st
from datetime import date, timedelta
import yfinance as yf
    
    
class RetirementCalculator:
    
    NUM_OF_DAYS_IN_A_YEAR = 365
    FAT_FIRE_MULTIPLE = 50
    PERCENTAGE_MULTIPLIER = 100
    AVERAGE_ANNUAL_INFLATION_RATE = 0.037
    
    class User:
        def __init__(self):
            self.annual_expenses = None
            self.current_age = None
            self.retirement_age = None
        
    def __init__(self):
        self.user = self.User()
        self.initialize_app()
    
    def initialize_app(self):
        st.title("Retirement Savings Calculator")
        st.write("This app calculates how much you need to save for retirement, adjusted for inflation, based on your annual expenses and planned retirement age.")
        
    def retrieve_user_info(self):
        self.user.annual_expenses = st.number_input(
            "**Please enter your estimated annual expenditure** (total yearly spending on living expenses, bills, and discretionary costs): $",
            min_value=0.0,
            step=1000.0,
            value=50000.0
            )
        self.user.current_age = st.number_input(
            "**Please enter your current age:**",
            min_value=0.0,
            step=1.0,
            value=18.0
            )
        self.user.retirement_age = st.number_input(
            "**Please enter your planned retirement age:**",
            min_value=self.user.current_age,
            step=1.0,
            value=65.0
            )
    
    def calculate(self):
        self.user.years_until_retirement = self.user.retirement_age - self.user.current_age
        self.user.retirement_amount_raw = self.user.annual_expenses * self.FAT_FIRE_MULTIPLE
        self.user.inflation_adjusted_retirement_amount = (self.user.retirement_amount_raw * 
                                                          ((1 + self.AVERAGE_ANNUAL_INFLATION_RATE) ** 
                                                           self.user.years_until_retirement))
    
    def display_results(self):
        st.subheader("Results")
        st.markdown(
            f"""
            <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; color: black;">
                <p>You would need to have saved a total of <strong>${self.user.inflation_adjusted_retirement_amount:,.2f}</strong> to retire comfortably {self.user.years_until_retirement} years from today (at the time of retirement). This amount is adjusted for inflation of {self.AVERAGE_ANNUAL_INFLATION_RATE * self.PERCENTAGE_MULTIPLIER:,.2f}% based on the average annual inflation in the United States over the past 200 years and reflects the future value, not the amount you need to have saved today.</p>
                <p>For context, the amount would be worth <strong>${self.user.retirement_amount_raw:,.2f}</strong> today.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    retirement_calculator = RetirementCalculator()
    retirement_calculator.retrieve_user_info()
    retirement_calculator.calculate()
    if st.button("Calculate"):
        retirement_calculator.display_results()


if __name__ == "__main__":
    main()