from A01_Log_Manager import *
import ccxt

# Taking my keys from local file
with open('../Secret/Key.sc') as f:
    Key = f.readlines()

loginfo('Reading keys from file ../Secret/Key.sc')

Key = [x.strip() for x in Key] 

# Logging in
Bin = ccxt.binance()
Bin.apiKey  = str(Key[0])
Bin.secret =  str(Key[1])

# Querying Account Balance
MyDict = Bin.fetch_ohlcv('ETH/BTC')

print('Results:')
type(MyDict)
