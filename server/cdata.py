import numpy as np
import loaddata as l
import pickle
from collections import defaultdict

aDict = defaultdict(lambda : defaultdict(lambda : {'strikePrices': [], 'quantities': [], 'avgStrike': 0, 'avgQuantity': 0}))

for trade in l.dictl:

    if trade['product_type'] == 'S':
        key1 = 'stocks'
        
    else:
        key1 = str(trade['product'])

    key2 = trade['buying_party']

    ref = aDict[key1][key2]
    
    ref['quantities'].append(trade['quantity'])
    ref['strikePrices'].append(trade['strike_price'])

# Can also do running average to perhaps lower time
for p in aDict.keys():
    for bp in aDict[p].keys():
        aDict[p][bp]['avgStrike'] = np.mean(aDict[p][bp]['strikePrices'])
        aDict[p][bp]['avgQuantity'] = np.mean(aDict[p][bp]['quantities'])

dict2 = {x:dict(y) for x, y in aDict.items()}

with open('aDict.p', 'wb') as handle:
    pickle.dump(dict2, handle, protocol=pickle.HIGHEST_PROTOCOL)