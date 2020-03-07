from os import listdir
from os.path import isfile, join
import datetime
from random import randint
from collections import defaultdict
import numpy as np
from math import floor,ceil
import pickle
trades = []
months = ['January','February','March','April','May','June','July','August','September','October','November','December']
import matplotlib.pyplot as plt


class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret


def iterateData(data_path=''):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    for x in range(2010,2020):
        for month in months:
            path = f'{data_path}/derivativeTrades/{x}/{month}'
            onlyfiles = sorted([join(path, f) for f in listdir(path) if isfile(join(path, f))])
            for csv in onlyfiles:
                with open(csv,'r') as f:
                    date = csv.split('\\')[-1] # My file system uses \ maybe yours uses /
                    lines = f.readlines()[1:]
                    currencyValues = {}
                    with open(f'{data_path}/currencyValues/{x}/{month}/{date}') as c:
                        b = c.readlines()[1:]
                        currencyValues = {line[1]: float(line[2]) for line in [x.split(",") for x in b]}
                    v = [line.split(",") for line in lines]
                    for line in v:
                        dt = [int(x) for x in line[0].split(' ')[0].split('/')]
                        mdt = [int(x) for x in line[8].split('/')]
                        data = {'date':datetime.date(dt[2],dt[1],dt[0]),
                                'tradeID':line[1],
                                'product':line[2],
                                'buyingParty':line[3],
                                'sellingParty':line[4],
                                'notionalAmount':float(line[5])/float(currencyValues[line[6]]),
                                'notionalCurrency':line[6],
                                'quantity':int(line[7]),
                                'maturityDate':datetime.date(mdt[2],mdt[1],mdt[0]),
                                'underLyingPrice':float(line[9])/currencyValues[line[10]],
                                'underLyingCurrency':line[10],
                                'strikePrice':float(line[11])/currencyValues[line[6]]
                                }
                        yield data

def main():
    productMetaData = {

    }
    runningMetaData = defaultdict(lambda : {'historicalPrice':[],'runningAvgClosePrice':0,'totalEntries':0,'runningAvgTradePrice':0,'runningAvgQuantity':0,'totalQuantity':0,'trades':0,'day':0})
    runningMetaData['INFO_DAY'] = 0

    availableDates = []

    variables = {
        'remembranceVariables':{
        'SMA' : 20,
        'TimePeriod':20},
    }
    #variables['memory'] = max(variables['remembranceVariables'],key=lambda x: variables['remembranceVariables'][x][1])[1]

    def funcOrNone(x,func):
        try:
            return func(x)
        except:
            return None

    trainingData = []#pickle.load(open('train.p','rb'))

    day = 0
    i=0

    rr = []
    for x in range(2010,2020):
        for month in months:
            path = '../../derivativeTrades/{}/{}'.format(x,month)
            onlyfiles = sorted([join(path,f) for f in listdir(path) if isfile(join(path, f))])
            print(onlyfiles)
            for csv in onlyfiles:
                date = csv.split('\\')[-1]
                availableDates.append(date)
                i+=1
                print(i/len(onlyfiles)/120*100)
                with open(csv,'r') as f:
                    runningMetaData['INFO_DAY'] += 1
                    day = runningMetaData['INFO_DAY']
                    currencyValues = {}
                    with open('../../data/currencyValues/{}/{}/{}'.format(x,month,date)) as c:
                        b = c.readlines()[1:]
                        currencyValues = {line[1]:float(line[2]) for line in [x.split(",") for x in b]}
                    lines = f.readlines()[1:]
                    v = [line.split(",") for line in lines]
                    productClosePrices = {}
                    stockClosePrices = {}
                    with open('../../data/productPrices/{}/{}/{}'.format(x,month,date)) as c:
                        productClosePrices = {l.split(',')[1]:float(l.split(',')[2].rstrip('\n')) for l in c.readlines()[1:]}
                    with open('../../data/stockPrices/{}/{}/{}'.format(x,month,date)) as c:
                        stockClosePrices = {l.split(',')[1]:float(l.split(',')[2].rstrip('\n')) for l in c.readlines()[1:]}
                    dayMetaData = keydefaultdict(lambda key: {'20DaySD':0,
                                                              'SMA': np.mean(runningMetaData[key]['historicalPrice'][-smaPeriod:]),
                                                       'UP': {'dayDifference': None,
                                                              'periodHigh': funcOrNone(runningMetaData[key]['historicalPrice'][floor(day/tp) * tp:],max),
                                                              'periodLow': funcOrNone(runningMetaData[key]['historicalPrice'][floor(day/tp) * tp:],min)
                                                              }, 'trades': 0, 'volume': 0})
                    for key,price in list(stockClosePrices.items()) + list(productClosePrices.items()):
                        r = runningMetaData[key]['runningAvgClosePrice']
                        n = runningMetaData[key]['totalEntries']
                        # Was adding average volume and average trade price
                        runningMetaData[key]['runningAvgClosePrice'] = (((r * n) + float(price)) / (n + 1))
                        runningMetaData[key]['totalEntries'] += 1
                        hp = runningMetaData[key]['historicalPrice']
                        runningMetaData[key]['historicalPrice'].append(price)
                        if len(hp) >= 20:
                            sma = dayMetaData[key]['SMA'] = np.mean(hp[-20:])
                            sd = np.std(hp[-20:])
                            dayMetaData[key]['20DaySD'] = sd
                        if len(hp) >=2:
                            dayMetaData[key]['UP']['dayDifference'] = hp[-1] - hp[-2]
                        # if len(runningMetaData[key]['historicalPrice']) > variables['memory']:
                        #      runningMetaData[key]['historicalPrice'] = runningMetaData[key]['historicalPrice'][1:]
                    tp = variables['remembranceVariables']['TimePeriod']
                    smaPeriod = variables['remembranceVariables']['SMA']
                    stocksSeen = {}
                    for line in v:
                        dt = [int(x) for x in line[0].split(' ')[0].split('/')]
                        mdt = [int(x) for x in line[8].split('/')]
                        data = {'date':datetime.date(dt[2],dt[1],dt[0]),
                                'tradeID':line[1],
                                'product':line[2],
                                'buyingParty':line[3],
                                'sellingParty':line[4],
                                'notionalAmount':float(line[5])/float(currencyValues[line[6]]),
                                'notionalCurrency':line[6],
                                'quantity':int(line[7]),
                                'maturityDate':datetime.date(mdt[2],mdt[1],mdt[0]),
                                'underLyingPrice':float(line[9])/currencyValues[line[10]],
                                'underLyingCurrency':line[10],
                                'strikePrice':float(line[11])/currencyValues[line[6]]
                        }
                        '''
                        0 date
                        1 tradeID
                        2 product
                        3 buyingParty
                        4 sellingParty
                        5 notionalAmount
                        6 notionalCurrency
                        7 quantity
                        8 maturityDate
                        9 underLyingPrice
                        10 underLyingCurrency
                        11 strikePrice
                        trades.append({
                            0'date': line[0],
                            1'product': line[2],
                            2'buyingParty': line[3],
                            3'sellingParty': line[4],
                            4'notionalAmount': currencyValues[line[6]] * float(line[5]),
                            5'notionalCurrency': line[6],
                            6'quantity': line[7],
                            7'maturityDate': line[8],
                            8'underlyingPrice': currencyValues[line[10]] * float(line[9]),
                            9'underlyingCurrency': line[10],
                            10'strikePrice': currencyValues[line[10]] * float(line[11])
                        })'''
                        isStock = (data['product'] == 'Stocks')
                        key = data['sellingParty'] if isStock else data['product']

                        q = runningMetaData[key]['runningAvgQuantity']
                        n = runningMetaData[key]['trades']
                        runningMetaData[key]['runningAvgQuantity'] = ((q * n) + data['quantity']) / (n + 1)
                        runningMetaData[key]['trades'] += 1
                        dayMetaData[key]['volume'] += data['quantity']
                        dayMetaData[key]['trades'] += 1
                        md = runningMetaData[key]
                        dmd = dayMetaData[key]
                        p = runningMetaData[key]['runningAvgTradePrice']
                        n = runningMetaData[key]['totalQuantity']
                        if key=='Blue Shells':
                            if data['strikePrice'] > 10000:
                                print()
                            rr.append(((data['maturityDate'] - datetime.date(2010, 1, 1)).days, data['strikePrice']))
                        runningMetaData[key]['runningAvgTradePrice'] = ((p * n) + (data['underLyingPrice'] * data['quantity'])) / (n + data['quantity'])
                        runningMetaData[key]['totalQuantity'] += data['quantity']

                        # defaultdict(lambda : {'historicalPrice':[],'runningAvgClosePrice':0,'totalEntries':0,'runningAvgTradePrice':0,'runningAvgQuantity':0,'totalQuantity':0,'trades':0})
                        addData = (
                            (data['date'] - data['maturityDate']).days,
                            data['quantity'],
                            data['underLyingPrice'],
                            data['strikePrice'],
                            md['runningAvgClosePrice'],
                            md['runningAvgQuantity'],
                            md['runningAvgTradePrice'],
                            dmd['20DaySD'],
                            dmd['SMA'],
                            dmd['UP']['dayDifference'],
                            dmd['UP']['periodHigh'],
                            dmd['UP']['periodLow']
                        )
                        if dmd['20DaySD'] > 0 and len(md['historicalPrice'])>10 and all([x not in [None,float('inf'),float('-inf'),np.nan] for x in addData]):
                            trainingData.append(addData)

    pickle.dump(dict(runningMetaData),open('runningMetaData.p','wb'))
    np.array(trainingData).dump('train.np')

if __name__ == "__main__":
    main()