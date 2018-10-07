import ccxt
import pandas as pd
import datetime as dt
import time as tm
from F_Log_Manager import *

class Exchanger:
    

    # 1.0 ========== Initiation ==========

    def __init__(self,File_Key='../Secret/Key.sc'):

        logdeb('-> Initiating exchanger')
        logdeb ('---> Reading keys from file ' + File_Key)
        
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
            logdeb('---> Key succesfully stored')

            # End of initiation
            Test_Info = self.Exc.load_time_difference()
            if Test_Info <= 0:
                raise Exception('--- !!! Time difference is not available!!!')

            logdeb('---> Time diference = '+str(Test_Info))
            loginfo('-> Exchanger succesfully initiated')

        except Exception as e:
            logerror(e)
            logerror('!!! Connection Failed: The exchanger could not be set up')
    
    # 2.0 ========== Get Balance data frame ==========
 
    def Get_Balance_DF(self):
        ''' 
        Returns the actual balance of the portfolio in the specified units
            Units: Name of the stock of the result
            Default units = Self (No transformation)
        '''
        # Trying to get the balance
        logdeb('-> Getting balance in USDT')
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

            # Adding info in USDT
            Market_DF = self.Market_Values_DF(Bal_DF.index.tolist())

            # Making the join and creating value in USDT
            Bal_DF = Bal_DF.join(Market_DF)
            Bal_DF['free_USD'] = Bal_DF['free']*Bal_DF['bid']
            Bal_DF['locked_USD'] = Bal_DF['locked']*Bal_DF['bid']
            Bal_DF['total_USD'] = Bal_DF['total']*Bal_DF['bid']
            Bal_DF = Bal_DF[['free_USD','locked_USD','total_USD']].sort_values('total_USD',ascending = 0)

            logdeb('-> Actual balance is:\n'+str(Bal_DF))
            return (Bal_DF)

        
        # Error handlign
        except Exception as e:
            logerror(e)
            logerror('!!! Balance fetching Failed')

    # 3.0 ========== Get Coin Market values in USD ==========
    
    def Market_Values_DF(self,Targets=['All']):
        '''
        Returns a data frame of pandas with the actual market exchange prices
        of the desired coins listed in "Targets" in the unit USDT
            Example: Targets=['BTC','ETH']
        '''
        logdeb('-> Extracting market values for Targets = ' + str(Targets))
        
        try:
            # Load market values
            MyDict = self.Exc.fetch_tickers()
            
            for Symbol in MyDict:
                del MyDict[Symbol]['info']
            
            # Put them in a DataFrame
            DF = pd.DataFrame.from_dict(MyDict,orient='index')
            DF['base'] = DF['symbol'].apply(lambda x: x.split('/')[0]) 
            DF['quote'] = DF['symbol'].apply(lambda x: x.split('/')[1]) 

            # I take non-zero values
            DF = DF[DF['bid'] > 0]
            # I take all pairs that goes for USDT and the rest that goes to BTC
            DF_USD=DF[DF['quote']=='USDT'][['base','quote','bid']]
            
            # I take the change to USDT of bitcoin to transform the pairs in BTC
            ChangeBTC = DF_USD[DF_USD['base']=='BTC']['bid'].values[0]
            logdeb('---> Change of BTC/USDT is = '+str(ChangeBTC))

            # I take the coins that I can only change to BTC
            DF_BTC=DF[~DF['base'].isin(DF_USD['base'])]
            DF_BTC=DF_BTC[DF_BTC['quote']=='BTC'][['base','quote','bid']]
            
            # I Transform them to USDT
            DF_BTC['bid']=DF_BTC['bid']*ChangeBTC
            DF_BTC['quote']='USDT'
            
            # I join the results and send them

            Union = [DF_BTC,DF_USD]
            Result = pd.concat(Union).reset_index()[['base','quote','bid']]
            logdeb('Market values obtained as: \n' + str(Result))
            if Targets==['All']:
                logdeb('-> Market values succesfuly generated')
                return(Result.set_index('base'))
            else:
                logdeb('-> Market values for ' + str(Targets) + ' succesfuly generated')
                return(Result[Result['base'].isin(Targets)].set_index('base'))

        except Exception as e:
            logerror('ERROR while creating Market Values DT')
            logerror(e)

    # 4.0 ========== Get History Market values for BTC/USDT ==========
    
    def Get_History_BTC(self, limit = 1000, time_frame = '1m'):
        
        try:
            logdeb('-> Getting history for BTC/USDT')
            # Fetch data from binance
            History = self.Exc.fetch_ohlcv('BTC/USDT',limit=limit, timeframe = time_frame)

            # Transform data to dataframe
            Final_Hist = pd.DataFrame(History, columns=['Date','o','h','l','c','v'])
            Final_Hist['Date'] = Final_Hist['Date'].apply(lambda x: dt.datetime.fromtimestamp(x/1000))
            Final_Hist['Coin'] = 'BTC';
            # Set Date as an index
            Final_Hist = Final_Hist.set_index(['Coin','Date'])


            # Return resuñts
            logdeb('-> Values correctly returned')
            return(Final_Hist)

        except Exception as e:

            logerror('ERROR while getting BTC hitory')
            logerror(e)

    # 5.0 ========== Get History Market values forany coin in USDT ==========

    def Get_History(self, Coins, limit = 1000, time_frame = '1m'):
        try:
            logdeb('-> Getting history for ' + str(Coins))

            # First get the indepent serie of BTC/USDT to transform the data
            History = self.Get_History_BTC(limit = limit, time_frame = time_frame) 
            BTCUSD = History.loc['BTC',:]

            maxdate = max(BTCUSD.index)
            mindate = min(BTCUSD.index)
            # Fetch data from binance
            for coin in Coins:

                # I do thid process for coins not bitcoin
                if coin != 'BTC':
                    logdeb('Fetching history for: \n' + 
                           '\t Coin       = ' + str(coin) + '\n' + 
                           '\t Limit      = ' + str(limit) + '\n' + 
                           '\t Time_Frame = ' + str(time_frame) + '\n ')
                    
                    Info = self.Exc.fetch_ohlcv(coin+'/BTC',limit=limit+5, timeframe = time_frame)
                    # I manipulate the columns names and values 
                    Temp = pd.DataFrame(Info, columns=['Date','o','h','l','c','v'])
                    Temp['Coin'] = coin
                    Temp['Date'] = Temp['Date'].apply(lambda x: dt.datetime.fromtimestamp(x/1000))
                    Temp = Temp[Temp['Date'] >= mindate]
                    Temp = Temp[Temp['Date'] <= maxdate]
                    # I set the coin as the first index
                    Temp = Temp.set_index(['Coin','Date'])
                        
                    # I Join the data by index Date
                    Join = [Temp,History]
                    History = pd.concat(Join)
             

            # I multiply coin values by BTC results
            def To_USD(row):
                if row['Coin'] != 'BTC':
                    date = min(row['Date'],maxdate)
                    row['o'] = row['o']*BTCUSD.loc[date]['o']
                    row['h'] = row['h']*BTCUSD.loc[date]['h']
                    row['l'] = row['l']*BTCUSD.loc[date]['l']
                    row['c'] = row['c']*BTCUSD.loc[date]['c']
                return(row)

            History = History.reset_index().apply(To_USD, axis = 1)       
            # Set Date as an index
            if 'BTC' not in Coins:
                History = History[History['Coin'] != 'BTC']
            History = History.set_index(['Coin','Date'])

            # Return results
            logdeb('-> Values correctly returned')
            return(History)

        except Exception as e:
            logerror('ERROR while getting ' + str(Coins) + ' hitory')
            logerror(e)
  

# Querying Account Balance
# Bin = Exchanger()
# List=['TUSD','BTC','ETH']
# # T=Bin.Get_History_BTC(limit = 5)
# # print(T)
# # print(T.loc['BTC'limit['o'])
# T = Bin.Get_History(List,limit = 10, time_frame='5m')
# print(T)






