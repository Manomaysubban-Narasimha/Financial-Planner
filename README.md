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

### 3. Obtain API Keys
- Visit newsapi.org and obtain NewsAPI Key
- Visit https://site.financialmodelingprep.com/ and obtain FMP API key

### 4. Create a folder for streamlit in the project's root directory and create secrets.toml file to store the API keys
```bash
mkdir .streamlit
cd .streamlit
touch secrets.toml
```

### 5. Fill the secrets.toml file with 
```bash 
news_api_key = "<Your NewsAPI Key>"
fmp_api_key = "<Your FMP API Key>"
``` 

### 6. Install Dependencies
```bash
pip install -r requirements.txt
```

### 7. Run the App
```bash
streamlit run app.py
```

Open your browser to http://localhost:8501 to access the app.
