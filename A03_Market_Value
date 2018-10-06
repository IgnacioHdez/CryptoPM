import ccxt
import pandas as pd
from A01_Log_Manager import *

def Market_Values_DF(Targets=['All']):
    '''
    Returns a data frame of pandas with the actual market exchange prices
    of the desired coins listed in "Targets" in the unit USDT
        Example: Targets=['BTC','ETH']
    '''
    logdeb('Extracting market values for Targets = ' + str(Targets))
    
    try:
        # Initiate a conection with binance
        Exc = ccxt.binance()
        
        # Load market values
        MyDict = Exc.fetch_tickers()
        
        for Symbol in MyDict:
            del MyDict[Symbol]['info']
        
        # Put them in a DataFrame
        DF = pd.DataFrame.from_dict(MyDict,orient='index')
        DF['base'] = DF['symbol'].apply(lambda x: x.split('/')[0]) 
        DF['quote'] = DF['symbol'].apply(lambda x: x.split('/')[1]) 
        
        # I take all pairs that goes for USDT and the rest that goes to BTC
        DF_USD=DF[DF['quote']=='USDT'][['base','quote','bid']]
        
        # I take the change to USDT of bitcoin to transform the pairs in BTC
        ChangeBTC = DF_USD[DF_USD['base']=='BTC']['bid'].values[0]
        logdeb('Change of BTC/USDT is = '+str(ChangeBTC))

        # I take the coins that I can only change to BTC
        DF_BTC=DF[~DF['base'].isin(DF_USD['base'])]
        DF_BTC=DF_BTC[DF_BTC['quote']=='BTC'][['base','quote','bid']]
        
        # I Transform them to USDT
        DF_BTC['bid']=DF_BTC['bid']*ChangeBTC
        DF_BTC['quote']='USDT'
        
        # I join the results and send them

        Union = [DF_BTC,DF_USD]
        Result = pd.concat(Union).reset_index()[['base','quote','bid']]
        if Targets==['All']:
            return(Result)
        else:
            return(Result[Result['base'].isin(Targets)])

    except Exception as e:
        logerror('ERROR while creating Market Values DT')
        logerror(e)

