import streamlit as st
import requests
from statistics import mean

SUCCESSFUL_REQUEST = 200


def get_average_recommendation_rating(stock_symbol):
    fmp_api_key = st.secrets["fmp_api_key"]
    url = f"https://financialmodelingprep.com/api/v3/rating/{stock_symbol}?apikey={fmp_api_key}"
    response = requests.get(url)
    if response.status_code == SUCCESSFUL_REQUEST:
        data = response.json()  # Parse the JSON response
        all_rating_scores = list()
        all_rating_scores.append(data[0]["ratingScore"])
        all_rating_scores.append(data[0]["ratingDetailsDCFScore"])  # Discounted Cash Flow
        all_rating_scores.append(data[0]["ratingDetailsROEScore"])  # Return on Equity
        all_rating_scores.append(data[0]["ratingDetailsROAScore"])  # Return on Assets 
        all_rating_scores.append(data[0]["ratingDetailsDEScore"])  # Debt to Equity 
        all_rating_scores.append(data[0]["ratingDetailsPEScore"])  # Price to Earnings
        all_rating_scores.append(data[0]["ratingDetailsPBScore"])  # Price to Book
        
        return round(mean(all_rating_scores), 5)
    else:
        print(f"Error unable to receive response")


def get_constituents():
    api_key = st.secrets["fmp_api_key"]

    url = f"https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey={api_key}" # Nasdaq100 constituents
    
    response = requests.get(url)
        
    constituents = response.json() # list of dictionaries with each dictionary consisting of keys: symbol, name, sector, subSector, headQuarter, dateFirstAdded, cik, founded

    # print(f"Date type = {type(data)} of {type(data[0])}")
    # print(f"Number of constituents = {len(data)}")
    # print(f"Data = {data}")
    symbol_rating = dict()
    for constituent in constituents:
        symbol = constituent['symbol']
        if symbol == "GOOG": # since GOOGL would be included, GOOG is not necessary and redundant. GOOGL provides the shareholder with one vote per share while GOOG does not, thus GOOGL is preferred over GOOG
            continue
        symbol_rating[symbol] = get_average_recommendation_rating(symbol)
    
    # Sort symbol_rating dictionary by values in descending order
    # Get net income for all symbols
    net_incomes = {}
    for symbol in symbol_rating.keys():
        url = f"https://financialmodelingprep.com/stable/income-statement?symbol={symbol}&apikey={api_key}"
        response = requests.get(url)
        if response.status_code == SUCCESSFUL_REQUEST:
            data = response.json()
            if data:  # Check if data exists
                net_incomes[symbol] = data[0]['netIncome']  # Get most recent net income
    
    # Sort by rating first, then by net income for ties, and get top 10
    sorted_symbol_rating = dict(list(sorted(symbol_rating.items(),
        key=lambda x: (x[1], net_incomes.get(x[0], 0)),
        reverse=True))[:10])
    print(f"Top 10 Recommended Companies:")
    for symbol, rating in sorted_symbol_rating.items():
        print(f"Symbol: {symbol}, Rating: {rating}, Net Income: ${net_incomes[symbol]:,.2f}")
    print()


def main():
    get_constituents()


if __name__ == "__main__":
    main()