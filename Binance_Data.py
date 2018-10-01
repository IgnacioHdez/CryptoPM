# -*- coding: utf-8 -*-

import os
import sys
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------

this_folder = os.path.dirname(os.path.abspath(__file__))
root_folder = os.path.dirname(os.path.dirname(this_folder))
sys.path.append(root_folder + '/python')
sys.path.append(this_folder)


import ccxt

binance = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'

index = 4  # use close price from each ohlcv candle

height = 15
length = 80


def print_chart(exchange, symbol, timeframe):

    print("\n" + exchange.name + ' ' + symbol + ' ' + timeframe + ' chart:')

    # get a list of ohlcv candles
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)

    # get the ohlCv (closing price, index == 4)
    series = [x[index] for x in ohlcv]

    
    plt.plot(series[-length:])  # print the chart
    plt.show()

    last = ohlcv[len(ohlcv) - 1][index]  # last closing price
    return last


last = print_chart(binance, symbol, timeframe)
print("\n" + binance.name + " ₿ = $" + str(last) + "\n")  # print last closing price
