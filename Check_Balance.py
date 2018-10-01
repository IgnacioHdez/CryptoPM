import ccxt

# Logging in
Bin = ccxt.binance()
Bin.apiKey  = 'FSTcZylTG87OtDnXLdYAvBgdqXPLesowPTqITz7IzK7HCPrMQMft9SZNSRjJMtx1'
Bin.secret = 'Uo1rIY3SsQAa4ApybU5VBXMkOvEjgFvRBSMXZNG3jHASKj8qjSgDgYAjNWlpEJfT'

# Querying Account Balance
MyDict = Bin.fetch_balance()


