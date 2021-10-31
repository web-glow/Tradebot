import websocket, json, pprint

crypto = "btcaud"
interval = "1m"
SOCKET = f"wss://stream.binance.com:9443/ws/{crypto}@kline_{interval}"

closes = []

# Trading Strategy Parameters
aroon_time_period = 14

core_to_trade = True
core_quantity = 0

amount = 1000
core_trade_amount = amount*0.80
trade_amount = amount*0.20
money_end = amount
portfolio = 0
investment, closes, highs, lows = [], [], [], []

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
    print('closed connection')

def on_message(ws, message):
    global closes, highs, core_to_trade, lows, core_trade_amount, core_quantity, money_end, portfolio, investment
    json_message = json.loads(message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    high = candle['h']
    low = candle['l']
    print(close)
    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        highs.append(float(high))
        lows.append(float(low))
        last_price = closes[-1]
        print(f'closes: {closes}')
        print(investment)
        if core_to_trade:
            buy(core_trade_amount, price = closes[-1])
            core_quantity += core_trade_amount / closes[-1]
            core_to_trade = False

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()


