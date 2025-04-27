import credentials as crs
from fyers_apiv3 import fyersModel
import pandas as pd
import numpy as np
import datetime as dt
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='short_strategy.log'
)

# Credentials
client_id = crs.client_id
secret_key = crs.secret_key
redirect_uri = crs.redirect_uri

with open('access.txt') as f:
    access_token = f.read()

list_of_stocks = ['SBIN']  # Add more stocks as needed
exchange = 'NSE'           # Exchange code
sec_type = 'EQ'            # Security type
list_of_tickers = {}

for t in list_of_stocks:
    ticker = f"{exchange}:{t}-{sec_type}"
    list_of_tickers.update({t: ticker})

# Timeframe and parameters
time_frame = 15  # 1-minute timeframe for analysis
days = 20       # 20 days of historical data
start_hour, start_min = 7, 30  # Strategy start time
end_hour, end_min = 15, 0      # Strategy end time

fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

def get_historical_data(ticker, interval, duration):
    try:
        data = {
            "symbol": ticker,
            "resolution": interval,
            "date_format": "1",
            "range_from": str(dt.date.today() - dt.timedelta(duration)),
            "range_to": str(dt.date.today()),
            "cont_flag": "1"
        }
        sdata = fyers.history(data)
        sdata = pd.DataFrame(sdata['candles'])
        sdata.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        sdata['date'] = pd.to_datetime(sdata['date'], unit='s')
        sdata.date = sdata.date.dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        sdata = sdata.set_index('date')
        
        # Calculate 200 EMA
        sdata['ema_200'] = sdata['close'].ewm(span=200, adjust=False).mean()
        
        return sdata
    except Exception as e:
        logging.error(f"Error fetching historical data: {e}")
        return None

def print_detailed_analysis(hist_df):
    """Detailed market analysis for debugging"""
    try:
        last_row = hist_df.iloc[-1]
        prev_row = hist_df.iloc[-2]
        
        logging.info("\n--- Detailed Market Analysis ---")
        logging.info(f"Previous Candle Close: {prev_row['close']}")
        logging.info(f"Previous Candle EMA 200: {prev_row['ema_200']}")
        logging.info(f"Current Candle Close: {last_row['close']}")
        logging.info(f"Current Candle EMA 200: {last_row['ema_200']}")
    except Exception as e:
        logging.error(f"Error in detailed analysis: {e}")

def short_entry_condition(hist_df):
    """Determine short entry conditions"""
    try:
        last_row = hist_df.iloc[-1]
        prev_row = hist_df.iloc[-2]
        
        # More flexible short entry condition
        short_entry = (
            # Previous close above EMA
            (prev_row['close'] > prev_row['ema_200']) and 
            
            # Current close below EMA
            (last_row['close'] < last_row['ema_200']) and 
            
            # Additional confirmation: Price movement
            (last_row['close'] - prev_row['close'] < 0)
        )
        
        # Logging for debugging
        if short_entry:
            logging.info("🔴 Short Entry Condition Met!")
            print_detailed_analysis(hist_df)
        else:
            logging.info("🟢 Short Entry Condition Not Met")
        
        return short_entry
    except Exception as e:
        logging.error(f"Error in short entry condition: {e}")
        return False

def trade_sell_stocks(stock_name, stock_price, quantity=2):
    """Place sell order"""
    try:
        data = {
            "symbol": stock_name,
            "qty": quantity,
            "type": 2,  # Market order
            "side": -1,  # Sell
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
            "stopLoss": 0,  # 2% stop loss
            "takeProfit": 0,# 2% take profit
        }
        response = fyers.place_order(data=data)
        logging.info(f"Short Entry Sell Order for {stock_name} at {stock_price}")
        logging.info(f"Sell Order Response: {response}")
        print(f"Short Entry Sell Order for {stock_name} at {stock_price}")
        print("Sell Order Response:", response)
    except Exception as e:
        logging.error(f"Error placing sell order: {e}")

def strategy_condition(hist_df, ticker):
    """Execute strategy conditions"""
    try:
        if short_entry_condition(hist_df):
            trade_sell_stocks(ticker, hist_df['close'].iloc[-1])
    except Exception as e:
        logging.error(f"Error in strategy condition: {e}")

def main_strategy():
    """Main trading strategy execution"""
    try:
        for ticker in list_of_tickers.values():
            hist_df = get_historical_data(ticker, f'{time_frame}', days)
            if hist_df is not None:
                strategy_condition(hist_df, ticker)
    except Exception as e:
        logging.error(f"Error in main strategy: {e}")

# Trading Loop
current_time = dt.datetime.now()
start_time = dt.datetime(current_time.year, current_time.month, current_time.day, start_hour, start_min)
end_time = dt.datetime(current_time.year, current_time.month, current_time.day, end_hour, end_min)

logging.info("Short Entry Strategy Initialized")
print("Short Entry Strategy Started")

while dt.datetime.now() < start_time:
    time.sleep(1)

while dt.datetime.now() < end_time:
    try:
        if dt.datetime.now().second in range(1, 3) and dt.datetime.now().minute % time_frame == 0:
            main_strategy()
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error in trading loop: {e}")

logging.info("End of Short Entry Trading Day")
print("End of Short Entry Trading Day")