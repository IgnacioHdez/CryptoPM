import cryptocmd as CMD
import matplotlib.pyplot as plt
import ccxt as ccxt

scrapper = CMD.CmcScraper('BTC')
Hist =scrapper.get_dataframe().set_index('Date')
print(Hist)
P1 = Hist.plot(y = 'Open')
P2 = Hist.plot(y = 'High')

# plt.show(P1)
plt.show(P2)
        


