import ccxt
import pandas as pd
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
 
    def Get_Balance_DF(self):

        # Trying to get the balance
        logdeb('Getting balance')
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
            return Bal_DF
        
        # Error handlign
        except Exception as e:
            logerror(e)
            logerror('!!! Balance fetching Failed')

        
# Querying Account Balance
Bin = Exchanger()
Bin.Get_Balance_DF()
