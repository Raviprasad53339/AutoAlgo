import credentials as crs
from fyers_apiv3 import fyersModel
import pandas as pd
import datetime as dt
import time
#credentials
# Replace these values with your actual API credentials
client_id = crs.client_id
secret_key = crs.secret_key
redirect_uri = crs.redirect_uri
with open('access.txt') as f:
    access_token=f.read()

list_of_stocks=['SBIN'] # Add more stocks as needed
exchange='NSE'          # Exchange code
sec_type='EQ'           # Security type

list_of_tickers={}

for t in list_of_stocks:
    ticker=f"{exchange}:{t}-{sec_type}"
    list_of_tickers.update({t:ticker})

print(list_of_tickers)

#timframe is 1 min
time_frame = 1                  # 1-minute timeframe for analysis
days = 20                       # 20 days of historical data
start_hour, start_min = 7, 30  # Start time for the strategy
end_hour, end_min = 15, 00      # End time for the strategy

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

'''
         a. Position and Order Management
get_open_position()       : Fetches all current open positions.
get_open_orders()         : Fetches all current open orders.
close_all_orders()        : Cancels all active orders.
close_ticker_open_orders(): Cancels active orders for a specific stock.
close_ticker_postion()    : Closes the open position for a specific stock.
'''
def get_open_position():
    position_response=fyers.positions()  ## This will provide all the position related information
    # print(position_response)
    if position_response['netPositions']:
        position_df=pd.DataFrame(position_response['netPositions'])
    else:
        position_df=pd.DataFrame()
    return position_df

def get_open_orders():
    order_response=fyers.orderbook()  ## This will provide all the order related information
    # print(order_response)
    if order_response['orderBook']:
        order_df=pd.DataFrame(order_response['orderBook'])
    else:
        order_df=pd.DataFrame()
    return order_df


def get_historical_data(ticker, interval, duration):
    """Extracts historical data and outputs in the form of a dataframe."""
    instrument = ticker
    data = {"symbol": instrument, "resolution": interval, "date_format": "1",
            "range_from": dt.date.today() - dt.timedelta(duration), "range_to": dt.date.today(), "cont_flag": "1"}
    sdata = fyers.history(data)
    # print(sdata)
    sdata = pd.DataFrame(sdata['candles'])
    sdata.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    sdata['date'] = pd.to_datetime(sdata['date'], unit='s')
    sdata.date = (sdata.date.dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata'))
    sdata['date'] = sdata['date'].dt.tz_localize(None)
    sdata = sdata.set_index('date')

    # Add 200 EMA using pandas built-in function instead of pandas_ta
    sdata['ema_200'] = sdata['close'].ewm(span=200, adjust=False).mean()
    return sdata



def close_all_orders():
    order_df=get_open_orders()
    if not order_df.empty:
        order_df=order_df[(order_df['status']==6) | (order_df['status']==4) | (order_df['status']==3)]
        if not order_df.empty :
            for id in order_df['id'].to_list():
                data = {"id":id}
                response = fyers.cancel_order(data=data)
                print(response)

def check_market_order_placed(ticker):
    order_df=get_open_orders()
    order_df=order_df[order_df['type']==2]
    order_df=order_df[(order_df['status']==6) | (order_df['status']==4) | (order_df['status']==3)]
    print(order_df)
    if not order_df.empty and (ticker in order_df['symbol'].to_list()):
       return 0
    else:
        return 1

def close_ticker_open_orders(ticker):

    order_df=get_open_orders()
    if not order_df.empty:
        order_df=order_df[(order_df['status']==6) | (order_df['status']==4) | (order_df['status']==3)]
        if (not order_df.empty) and (ticker in order_df['symbol'].to_list()):
            id=order_df[order_df['symbol']==ticker]['id'].iloc[0]
            data = {"id":id}
            response = fyers.cancel_order(data=data)
            print(response)
            
        else:
            print('no order to close')


def close_ticker_postion(name):
    position_df=get_open_position()
    if (not position_df.empty) and (name in position_df['symbol'].to_list()):
        id=position_df[position_df['symbol']==name]['id'].iloc[0]
        data = {
            "id":id
        }
        print(data)
        response = fyers.exit_positions(data=data)
        print(response)
        print('position closed')
    else:
        print('position does not exist')
 


def trade_buy_stocks(stock_name,stock_price,quantity=1):
    if check_market_order_placed(ticker):
        data = {
            "symbol":stock_name,
            "qty":quantity,
            "type":2, # Market order
            "side":1, # Buy
            "productType":"INTRADAY",
            "limitPrice":0,
            "stopPrice":0,
            "validity":"DAY",
            "disclosedQty":0,
            "offlineOrder":False,
            "stopLoss":0,    #"stopLoss": stock_price * 0.95,  # Set stop loss at 5% below price
            "takeProfit":0   #"takeProfit": stock_price * 1.05  # Set take profit at 5% above price
        }

        response3 = fyers.place_order(data=data)
        print("Buy Order Response:", response3)


# Updated trade_sell_stocks() with dynamic stop-loss and take-profit
def trade_sell_stocks(stock_name, stock_price, quantity=1):
    """Place a sell order with market order."""
    if check_market_order_placed(stock_name):
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
            "stopLoss":0, #stock_price * 1.05,  # Set stop loss at 5% above the stock price
            "takeProfit":0 #stock_price * 0.95  # Set take profit at 5% below the stock price
        }
        response3 = fyers.place_order(data=data)
        print("Sell Order Response:", response3)


        # if response3['s']=='ok':
        #     a=[stock_name,stock_price,'BUY',quantity_] 
       
        #     print('call buy condition satisfied')

        #     #placing stop order
        #     data = {
        #     "symbol":stock_name,
        #     "qty":quantity,
        #     "type":3,
        #     "side":-1,
        #     "productType":"INTRADAY",
        #     "limitPrice":0,
        #     "stopPrice":int(stock_price*0.90),
        #     "validity":"DAY",
        #     "disclosedQty":0,
        #     "offlineOrder":False,
        #     "orderTag":"tag1"
        #     }
        #     response3 = fyers.place_order(data=data)
        #     print(response3)

        # else:
            
        #     print('order did not go through')


def strategy_condition(hist_df,ticker):
    print('inside strategy conditional code ')
    # print(hist_df)
    print(ticker)
    buy_condition = (hist_df['close'].iloc[-1] > hist_df['ema_200'].iloc[-1]) and \
                (hist_df['close'].iloc[-2] <= hist_df['ema_200'].iloc[-2])
    if buy_condition:
        stop_loss = min(hist_df['low'].iloc[-2], hist_df['low'].iloc[-3])  # Lowest of the last two candles
        target = hist_df['close'].iloc[-1] + 2 * (hist_df['close'].iloc[-1] - stop_loss)
        trade_buy_stocks(ticker, hist_df['close'].iloc[-1], stop_loss, target)

    money = int(fyers.funds()['fund_limit'][0]['equityAmount'])
    money=money/1 #dividing money into 3 parts #Dynamically divides by the number of stocks
    print(money)
    closing_price=hist_df['close'].iloc[-1]
    if money>closing_price:
        if buy_condition:
            print('buy condition satisfied')
            trade_buy_stocks(ticker,closing_price)
        else:
            print('no condition satisfied')
    else:
        print('we dont have enough money to trade')


def main_strategy():
    pos_df= get_open_position()
    ord_df= get_open_orders()
    print(pos_df)
    print(ord_df)

    for ticker in list_of_tickers.values():
        print(ticker)
        #historical data with indicator data
        hist_df=get_historical_data(ticker,f'{time_frame}',days)
        # print(hist_df)

        money = int(fyers.funds()['fund_limit'][0]['equityAmount'])
        money = money / 1  # Or just `money = int(fyers.funds()['fund_limit'][0]['equityAmount'])`
                           #dividing money into 3 parts #Dynamically divides by the number of stocks
        print(money)
        closing_price=hist_df['close'].iloc[-1]
        print(closing_price)
        quantity=money/closing_price
        print(quantity)

        if quantity<1:
            continue

        if pos_df.empty:
            print('we dont have any position')
            strategy_condition(hist_df,ticker)

        elif len(pos_df)!=0 and ticker not in pos_df['symbol'].to_list():
            print('we have some position but ticker is not in pos')
            strategy_condition(hist_df,ticker)
        

        elif len(pos_df)!=0 and ticker in pos_df['symbol'].to_list():
            print('we have some pos and ticker is in pos')
            curr_quant=float(pos_df[pos_df['symbol']==ticker]['qty'].iloc[-1])
            print(curr_quant)

            if curr_quant==0:
                print('my quantity is 0')
                strategy_condition(hist_df,ticker)

            elif curr_quant>0:
                print('we are already long')
                # Sell Entry
                sell_condition = (hist_df['close'].iloc[-1] < hist_df['ema_200'].iloc[-1]) and \
                                (hist_df['close'].iloc[-2] >= hist_df['ema_200'].iloc[-2])
                if sell_condition:
                    print('sell condition is satisfied ')
                    trade_sell_stocks(ticker, closing_price)
                else:
                    print('sell condition not satisfied')


current_time=dt.datetime.now()
print(current_time)

start_time=dt.datetime(current_time.year,current_time.month,current_time.day,start_hour,start_min)
end_time=dt.datetime(current_time.year,current_time.month,current_time.day,end_hour,end_min)

print(start_time)
print(end_time)


#pre hour and post hour

while dt.datetime.now()<start_time :
    print(dt.datetime.now())
    time.sleep(1)

print('we have reached start time ')
print('we are running our strategy now')


while True:
    if dt.datetime.now()>end_time:
        break
    ct=dt.datetime.now()
    print(ct)
    if ct.second in range(1,3) and ct.minute in range(0,60,time_frame):
        main_strategy()
    time.sleep(1)



print('we have reached end time')


response = fyers.exit_positions(data={})
print(response)
#closing all orders
close_all_orders()
