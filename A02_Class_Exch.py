import ccxt
import pandas as pd
import datetime as dt
import time as tm
from A01_Log_Manager import *

class Exchanger:
    

    # 1.0 ========== Initiation ==========

    def __init__(self,File_Key='../Secret/Key.sc'):

        logdeb('Initiating exchanger')
        logdeb ('--- Reading keys from file ' + File_Key)
        
        try:
            # Opening file of keys
            with open('../Secret/Key.sc') as f:
                Key = f.readlines()
            Key = [x.strip() for x in Key] 

            # Loading the exchanger with the keys
            self.Exc = ccxt.binance()

            # Loading the keys
            self.Exc.apiKey  = str(Key[0])
            self.Exc.secret =  str(Key[1])
            logdeb('--- Key succesfully stored')

            # End of initiation
            Test_Info = self.Exc.load_time_difference()
            if Test_Info <= 0:
                raise Exception('--- !!! Time difference is not available!!!')

            logdeb('--- Time diference = '+str(Test_Info))
            loginfo('Exchanger succesfully initiated')

        except Exception as e:
            logerror(e)
            logerror('!!! Connection Failed: The exchanger could not be set up')
    
    # 2.0 ========== Get Balance data frame ==========
 
    def Get_Balance_DF(self, Units = 'Self'):
        ''' 
        Returns the actual balance of the portfolio in the specified units
            Units: Name of the stock of the result
            Default units = Self (No transformation)
        '''
        # Trying to get the balance
        logdeb('Getting balance in Units: ' + Units)
        try:
            # Loading Balance from exchanger
            Balance = self.Exc.fetch_balance()['info']['balances']
            
            # Transforming balance into a data frame and creating column TOTAL
            Bal_DF = pd.DataFrame.from_dict(Balance)
            Bal_DF[['free','locked']] = Bal_DF[['free','locked']].apply(pd.to_numeric)
            Bal_DF['total'] = Bal_DF['free']+Bal_DF['locked']

            Bal_DF = Bal_DF.set_index('asset')
            # Filtering rows with total = 0
            Bal_DF = Bal_DF[Bal_DF['total'] > 0]
            logdeb('--- Actual balance is:\n'+str(Bal_DF))
            if Units == 'Self':
                return Bal_DF
            else:
                # If Units is specified we need to get the actual market values
                print('Not ready')
        
        # Error handlign
        except Exception as e:
            logerror(e)
            logerror('!!! Balance fetching Failed')

    # 3.0

        
# Querying Account Balance
Bin = Exchanger()
Bin.Get_Balance_DF()

s = dt.datetime(year = 2018, month = 10, day = 4)
Tini = int(s.timestamp())*1000
Tfin = int(dt.datetime.now().timestamp()*1000) 

a=Bin.Exc.fetch_ohlcv('BTC/USDT',since=Tini,limit=10000)
Test = pd.DataFrame(a, columns=['Date','o','h','l','v','c'])
Test['Date'] = Test['Date'].apply(lambda x: dt.datetime.fromtimestamp(x/1000))

print(Test)
