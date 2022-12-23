# Script to query the option chain data from NSE and store it in a csv file

import requests
import pandas as pd
import datetime
import time
import os


# Function to get the option chain data from NSE
def get_option_chain_data(symbol):
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=" + symbol
    # Add a header and change the user agent to avoid 403 error
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Origin": "https://www.nseindia.com",
        "Referer": "https://www.nseindia.com/products/content/derivatives/equities/homepage_fo.htm",
    }

    print("Getting data for " + symbol)
    print(url)
    # Add exception handling
    try:
        r = requests.get(url, headers=headers, timeout=60)
    except Exception as e:
        print("Error: " + str(e))
        return None

    # Check if the response is 200
    if r.status_code != 200:
        print("Error: " + str(r.status_code))
        return None

    data = r.json()
    return data


# Parse the data
def parse_data(data, symbol):
    """
    data = {
    "records": {
        "expiryDates": [
            "22-Dec-2022",
            "29-Dec-2022",
            "05-Jan-2023",
            "12-Jan-2023",
            "19-Jan-2023",
            "25-Jan-2023",
            "02-Feb-2023",
            "09-Feb-2023",
            "23-Feb-2023",
            "29-Mar-2023",
            "29-Jun-2023",
            "28-Sep-2023",
            "28-Dec-2023",
            "27-Jun-2024",
            "26-Dec-2024",
            "26-Jun-2025",
            "24-Dec-2025",
            "25-Jun-2026",
            "31-Dec-2026",
            "24-Jun-2027"
        ],
        "data": [
            {
                "strikePrice": 7500,
                "expiryDate": "29-Dec-2022",
                "PE": {
                    "strikePrice": 7500,
                    "expiryDate": "29-Dec-2022",
                    "underlying": "NIFTY",
                    "identifier": "OPTIDXNIFTY29-12-2022PE7500.00",
                    "openInterest": 91,
                    "changeinOpenInterest": 0,
                    "pchangeinOpenInterest": 0,
                    "totalTradedVolume": 2,
                    "impliedVolatility": 193.52,
                    "lastPrice": 0.4,
                    "change": 0,
                    "pChange": 0,
                    "totalBuyQuantity": 1400,
                    "totalSellQuantity": 200,
                    "bidQty": 500,
                    "bidprice": 0.25,
                    "askQty": 100,
                    "askPrice": 1.7,
                    "underlyingValue": 18112.4
                }
            }]}}
    """
    option_data = data["records"]["data"]
    expiry_dates = data["records"]["expiryDates"]
    df = pd.DataFrame()
    for expiry_date in expiry_dates:
        for option in option_data:
            if option["expiryDate"] == expiry_date:
                if "CE" in option:
                    ce = option["CE"]
                    ce["option_type"] = "CE"
                    ce["expiry_date"] = expiry_date
                    ce["symbol"] = symbol
                    df = df.append(ce, ignore_index=True)
                if "PE" in option:
                    pe = option["PE"]
                    pe["option_type"] = "PE"
                    pe["expiry_date"] = expiry_date
                    pe["symbol"] = symbol
                    df = df.append(pe, ignore_index=True)
    df["timestamp"] = datetime.datetime.now()
    df = df[
        [
            "timestamp",
            "symbol",
            "expiry_date",
            "option_type",
            "strikePrice",
            "openInterest",
            "changeinOpenInterest",
            "pchangeinOpenInterest",
            "totalTradedVolume",
            "impliedVolatility",
            "lastPrice",
            "change",
            "pChange",
            "totalBuyQuantity",
            "totalSellQuantity",
            "bidQty",
            "bidprice",
            "askQty",
            "askPrice",
            "underlyingValue",
        ]
    ]
    df.columns = [
        "timestamp",
        "symbol",
        "expiry_date",
        "option_type",
        "strike_price",
        "open_interest",
        "change_in_open_interest",
        "p_change_in_open_interest",
        "total_traded_volume",
        "implied_volatility",
        "last_price",
        "change",
        "p_change",
        "total_buy_quantity",
        "total_sell_quantity",
        "bid_qty",
        "bid_price",
        "ask_qty",
        "ask_price",
        "underlying_value",
    ]

    return df


# Function to store the data in a csv file
def store_data(df, symbol):
    if os.path.exists("option_chain_data.csv"):
        df.to_csv("option_chain_data.csv", mode="a", header=False, index=False)
    else:
        df.to_csv("option_chain_data.csv", index=False)


# Function to get the option chain data for a list of symbols
def get_option_chain_data_for_list(symbols):
    for symbol in symbols:
        data = get_option_chain_data(symbol)

        # Check if the data is None
        if data is None:
            continue
        df = parse_data(data, symbol)
        store_data(df, symbol)
        time.sleep(10)


# List of symbols
symbols = ["NIFTY", "BANKNIFTY"]

# Get the option chain data for the list of symbols
get_option_chain_data_for_list(symbols)
