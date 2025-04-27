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
    filename='long_strategy.log'
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

def long_entry_condition(hist_df):
    """Determine long entry conditions"""
    try:
        last_row = hist_df.iloc[-1]
        prev_row = hist_df.iloc[-2]
        
        # More flexible long entry condition
        long_entry = (
            # Previous close below EMA
            (prev_row['close'] < prev_row['ema_200']) and 
            
            # Current close above EMA
            (last_row['close'] > last_row['ema_200']) and 
            
            # Additional confirmation: Price movement
            (last_row['close'] - prev_row['close'] > 0)
        )
        
        # Logging for debugging
        if long_entry:
            logging.info("🟢 Long Entry Condition Met!")
            print_detailed_analysis(hist_df)
        else:
            logging.info("🔴 Long Entry Condition Not Met")
        
        return long_entry
    except Exception as e:
        logging.error(f"Error in long entry condition: {e}")
        return False

def trade_buy_stocks(stock_name, stock_price, quantity=1):
    """Place buy order"""
    try:
        data = {
            "symbol": stock_name,
            "qty": quantity,
            "type": 2,  # Market order
            "side": 1,  # Buy
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
            "stopLoss": 0,  # 2% stop loss
            "takeProfit": 0,  # 2% take profit
        }
        response = fyers.place_order(data=data)
        logging.info(f"Long Entry Buy Order for {stock_name} at {stock_price}")
        logging.info(f"Buy Order Response: {response}")
        print(f"Long Entry Buy Order for {stock_name} at {stock_price}")
        print("Buy Order Response:", response)
    except Exception as e:
        logging.error(f"Error placing buy order: {e}")

def strategy_condition(hist_df, ticker):
    """Execute strategy conditions"""
    try:
        if long_entry_condition(hist_df):
            trade_buy_stocks(ticker, hist_df['close'].iloc[-1])
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

logging.info("Long Entry Strategy Initialized")
print("Long Entry Strategy Started")

while dt.datetime.now() < start_time:
    time.sleep(1)

while dt.datetime.now() < end_time:
    try:
        if dt.datetime.now().second in range(1, 3) and dt.datetime.now().minute % time_frame == 0:
            main_strategy()
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error in trading loop: {e}")

logging.info("End of Long Entry Trading Day")
print("End of Long Entry Trading Day")