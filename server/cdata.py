import numpy as np
import loaddata as l
from collections import defaultdict
    
usps = set()
sellingParties = defaultdict(list)

runningMetaData = defaultdict(lambda : {'quantities': [], 'historicalPrice': [], 'avgClosePrice': 0, 'totalEntries': 0, 'avgTradePrice': 0, 'avgQuantity': 0,'totalQuantity':0,'trades':0})

filter_keys = ['trade_id', 'product_type', 'date_of_trade', 'selling_party', 'quantity']



for trade in l.dictl:
    
    # Only do for stocks currently
    if trade['product_type'] == 'S':
        key = trade['selling_party']
        rmd = runningMetaData[key]

        q = rmd['avgQuantity']
        n = rmd['trades']

        rmd['avgQuantity'] = ((q * n) + trade['quantity']) / (n + 1)
        rmd['trades'] += 1
        rmd['totalQuantity'] += trade['quantity']
        rmd['quantities'].append(trade['quantity'])

    

print(np.mean(runningMetaData['VVBY18']['quantities']))
print(runningMetaData['VVBY18']['avgQuantity'])

# newdict = defaultdict(list)

# for stock in stocks:
#     for k in stock:
#         newdict[k].append(stock[k])
    

# uniqueSellingParties = set(newdict['selling_party'])

# sellingParties = defaultdict(list)

# for usp in uniqueSellingParties:
#     for stock in stocks:
#         if stock['selling_party'] == usp:
#             sellingParties[usp].append(stock)

# for usp in uniqueSellingParties:
#     quantities = []
#     for d in sellingParties[usp]:
#         quantities.append(d['quantity'])
#     print(np.mean(quantities))
        
