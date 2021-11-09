import websocket, json, pprint, talib
import numpy as np

crypto = "ethaud"
interval = "1m"
SOCKET = f"wss://stream.binance.com:9443/ws/{crypto}@kline_{interval}"

closes = []

# Trading Strategy Parameters
aroon_time_period = 10

core_to_trade = True
core_quantity = 0

amount = 1000
core_trade_amount = amount*0.20
trade_amount = amount*0.80
money_end = amount
portfolio = 0
investment, closes, highs, lows = [], [], [], []
real_time_portfolio_value = []
trade_amt = 0

# Paper trading simulation functions
def buy(allocated_money, price):
    global money_end, portfolio, investment

    quantity = allocated_money / price
    money_end -= quantity*price
    portfolio += quantity

    if investment == []:
        investment.append(allocated_money)
    else:
        investment.append(allocated_money)
        investment[-1] += investment[-2]

def sell(allocated_money, price):
    global money_end, portfolio, investment

    quantity = allocated_money / price
    money_end += quantity*price
    portfolio -= quantity
    investment.append(-allocated_money)
    investment[-1] += investment[-2]
    

def on_open(ws):
    print('opened connection')

def on_close(ws):
    global money_end
    portfolio_value = portfolio*closes[-1]
    if portfolio_value > 0:
        sell(portfolio_value, price = closes[-1])
    else:
        buy(-portfolio_value, price = closes[-1])
    money_end += investment[-1]
    print(f'portfolio: {portfolio}')
    print('All trades setteled')

def on_message(ws, message):
    global closes, highs, core_to_trade, lows, core_trade_amount, core_quantity, money_end, portfolio, investment, trade_amt
    json_message = json.loads(message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    high = candle['h']
    low = candle['l']
    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        highs.append(float(high))
        lows.append(float(low))
        last_price = closes[-1]
        

        if core_to_trade:
            buy(core_trade_amount, price = closes[-1])
            print(f'Core Investment: We bought ${core_trade_amount} worth of bitcoin', '\n')
            print("___________________________________________________________________")
            core_quantity += core_trade_amount / closes[-1]
            core_to_trade = False

        aroon = talib.AROONOSC(np.array(highs), np.array(lows), aroon_time_period)
        last_aroon = round(aroon[-1],2)
        #recommended exposure using aroon technical indicator
        #if last_aroon = 100 then the buy amount would be 100% of the trade_amount
        amt = last_aroon * trade_amount / 100
        port_value = portfolio*last_price - core_quantity*last_price
        # if trade_amt is negetive, we sell, if it is positive we buy
        trade_amt = amt - port_value

        RT_portfolio_value = port_value + core_quantity*last_price + money_end
        real_time_portfolio_value.append(float(RT_portfolio_value))
        print(f'the Last Aroon is "{last_aroon}" and recommended exposure is "${amt}"')
        print(f'Real-Time Portfolio value: ${RT_portfolio_value}', '\n')
        
        if trade_amt > 0:
            buy(trade_amt, price = last_price)
            print(f'We bought ${trade_amt} worth of bitcoin!!', '\n', '\n')
        elif trade_amt < 0:
            sell(-trade_amt, price = last_price)
            print(f'We sold ${trade_amt} worth of bitcoin!!', '\n', '\n')

       



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()


