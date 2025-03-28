# Financial Planner

A multi-page Streamlit application designed to assist with personal finance and investment decisions. The app includes four fully functional tools: Stock Recommender, Stock Analyzer, Portfolio Value Estimator, and Retirement Calculator.

## Features

- **Stock Recommender**: Get basic stock recommendations based on P/E ratio and dividend yield using real-time data from Yahoo Finance.
- **Stock Analyzer**: Visualize a stock's historical price performance over the past year.
- **Portfolio Value Estimator**: Calculate the total value of your stock portfolio based on current market prices.
- **Retirement Calculator**: Estimate your future savings based on current savings, monthly contributions, and expected returns.

## Prerequisites

- Python 3.9+ 
- Git
- A GitHub account (for hosting and version control)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Manomaysubban-Narasimha/Financial-Planner.git
cd financial-planner
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
streamlit run app.py
```

Open your browser to http://localhost:8501 to access the app.
