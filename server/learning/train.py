import pickle
import numpy as np
import pandas as pd
from keras.layers import Input, Dense
from keras.models import Model
import keras.losses
from os import listdir
from keras.models import load_model
from sklearn.metrics import mean_squared_error
from random import shuffle, randint
import tensorflow as tf
import datetime
import time
from math import floor,log2,fabs
from sklearn.cluster import DBSCAN
from random import random
setattr(tf.contrib.rnn.GRUCell, '__deepcopy__', lambda self, _: self)
setattr(tf.contrib.rnn.BasicLSTMCell, '__deepcopy__', lambda self, _: self)
setattr(tf.contrib.rnn.MultiRNNCell, '__deepcopy__', lambda self, _: self)



def printExample(x,enc):
    x = np.array([x])
    enc = enc.predict(x)
    for i in range(len(x[0])):
        print(f'{i} : {x[0][i]}, {enc[0][i]}, {(x[0][i] - enc[0][i])**2}')
    print(f'Total MSE, {mean_squared_error(x,enc)}')

#trainedData = pickle.load(open('trained.p','rb'))
#normalizedData = []

def loadData(normalized=False,test=0):
    trainingData = [x for x in np.load('trainedNN.np' if normalized else 'train.np',allow_pickle=True) if not normalized or all([y<1.5 and y>-1.5 for y in x])]
    if not normalized:
        shuffle(trainingData)
    if test>0:
        testData = trainingData[-test:]
        trainingData = trainingData[:-test]
    return (trainingData,testData) if test >0 else trainingData

#autoencoder = load_model('aec.h5')
#decoder = load_model('dec.h5')


#print(decoder.predict(autoencoder.predict(np.array([trainingData[-1]]))))
print()




#testData = trainingData[50000:58000]
#trainingData = trainingData[:50000] + trainingData[58000:]
#print(len(trainingData))

'''
addData = (
    0(data['date'] - data['maturityDate']).days, -- normalize by max day
    1data['quantity'], -- divide by average quantity
    2data['underLyingPrice'], -- divide by SMA?
    3data['strikePrice'], -- divide by max / divide by average then maybe logarithmic?
    4md['runningAvgClosePrice'], -- get rid? else 
    5md['runningAvgQuantity'], -- get rid
    6md['runningAvgTradePrice'], -- divide by 
    7dmd['20DaySD'], -- divide by SMA
    8dmd['SMA'], -- Divide by average price (small for some reason)
    9dmd['UP']['dayDifference'], -- divide by SMA
    10dmd['UP']['periodHigh'], -- divide by SMA
    11dmd['UP']['periodLow'] -- Divide by SMA
)'''
#runningMetaData = defaultdict(lambda : {'historicalPrice':[],'runningAvgClosePrice':0,'totalEntries':0,'runningAvgTradePrice':0,'runningAvgQuantity':0,'totalQuantity':0,'trades':0})

'''addData = (
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
)'''

variables = {
    'remembranceVariables':{
    'SMA' : 20,
    'TimePeriod':20}
}
def funcOrNone(x,func):
    try:
        return func(x)
    except:
        return None

def normalizeDatum(data, runningMetaData=pickle.load(open('runningMetaData.p','rb'))):
    isStock = (data['product'] == 'Stocks')
    key = data['sellingParty'] if isStock else data['product']
    md = runningMetaData[key]
    hp = runningMetaData[key]['historicalPrice']
    smaPeriod = 20
    day = runningMetaData['INFO_DAY']
    tp = 20
    dmd = {'20DaySD': np.std(hp[-smaPeriod:]),'SMA': np.mean(hp[-smaPeriod:]),'UP': {'dayDifference': hp[-1] - hp[-2],'periodHigh': funcOrNone(hp[floor(day / tp) * tp:], max),'periodLow': funcOrNone(hp[floor(day / tp) * tp:], min)}}
    #print(dmd)
    #print(md)
    d = (
        (data['date'] - data['maturityDate']).days,
        data['quantity'],
        data['underLyingPrice'],
        data['strikePrice'] / dmd['SMA'],
        md['runningAvgClosePrice'],
        md['runningAvgQuantity'],
        md['runningAvgTradePrice'],
        dmd['20DaySD'],
        dmd['SMA'],
        dmd['UP']['dayDifference'],
        dmd['UP']['periodHigh'],
        dmd['UP']['periodLow'])
    minDay =-2191.0
    maxStrikePrice = 1.4
    toAdd = (d[0] / minDay,
             d[1] / d[5],
             (d[2] / d[8] - 1) * 15,
             d[3] / maxStrikePrice,
             (d[7] / d[8] * 40) - 1,
             # (d[8] / d[6]) / maxSmaSD,
             (d[9] / d[8]) * 10,
             (d[10] / d[8] - 1) * 15,
             (d[11] / d[8] - 1) * 15)
    return toAdd


def normalizeData(trainingData):
    normalizedData = []
    days = [x[0] for x in trainingData]
    minDay = min(days) # -2191.0
    for x in range(len(trainingData)):
        l = list(trainingData[x])
        l[3] = trainingData[x][3] / trainingData[x][8]
        trainingData[x] = tuple(l)
    maxStrikePrice =  1.4
    #maxSmaSD = max([x[8]/x[6] for x in trainingData])
    l = len(trainingData)
    interval = floor(l / 100)
    for d in range(l):
        if d % interval == 0:
            print(d/l)
        d = trainingData[d]
        toAdd = (d[0] / minDay,
                 d[1] / d[5],
                 (d[2] / d[8] - 1) * 15,
                 d[3] / maxStrikePrice,
                 (d[7] / d[8] * 40) - 1,
                 #(d[8] / d[6]) / maxSmaSD,
                 (d[9] / d[8]) * 10,
                 (d[10] / d[8] - 1) * 15,
                 (d[11] / d[8] - 1) * 15)
        if all([y<1.5 and y>-1.5 for y in toAdd]):
            normalizedData.append(toAdd)
    print(f'Dropped rate : {len(normalizedData)/l}')
    return normalizedData

def saveTrainData(data,normalized=False):
    np.array(data).dump('trainedNN.np' if normalized else 'train.np')

def createModel():
    encodingDim = 3
    inputs = Input(shape=(8,))
    encoded = Dense(7,activation='sigmoid')(inputs)
    encoded = Dense(encodingDim,activation='relu')(encoded)
    decoded = Dense(7,activation='relu')(encoded)
    final = Dense(8,activation='tanh')(decoded)
    autoencoder = Model(inputs, final)
    encoder = Model(inputs,encoded)
    #decoder = Model(Input,final)
    return autoencoder,encoder

def trainModel(model,data,epochs,batch_size):
    data = np.array(data)
    model.compile(optimizer='adam', loss='mse')
    model.fit(data, data, epochs=epochs, batch_size=batch_size, shuffle=True)

def sampleErrorRatios(autoencoder):
    t = []
    l = len(trainingData)
    i = 0
    inter = floor(l / 1000)
    for x in trainingData[:10000]:
        i += 1
        if i % inter == 0:
            print(i / l)
        t.append(mean_squared_error(autoencoder.predict(np.array([x])), np.array([x])))
    a = sorted(t)
    print(a[floor(len(a) * 0.95)])
    print(a[floor(len(a) * 0.8)])
    print(a[floor(len(a) * 0.6)])

def estimateErrorRatio(errorValue):
    values = {0.95:0.037751311451393696,
    0.8:0.02520727266310019,
    0.6:0.01780338673080255}
    if errorValue > values[0.6] and errorValue < values[0.8]:
        return 0.6 + (0.2*((errorValue - values[0.6])/(values[0.8]-values[0.6])))
    if errorValue > values[0.8] and errorValue < values[0.95]:
        return 0.8 + (0.15*((errorValue - values[0.8])/(values[0.95]-values[0.8])))
    if errorValue > values[0.95]:
        return 1
    if errorValue < values[0.6]:
        return 0
def saveModel(autoencoder,encoder):
    code = str(randint(1,10000000)) + ".h5"
    encoder.save(r'mlModels/Encoder/' + code)
    autoencoder.save(r'mlModels/AutoEncoder/' + code)
def getModels():
    return listdir(r'D:\Users\jinxsimpson\Downloads\アニプログ\Softeng\mlModels\AutoEncoder')

def loadModel(code):
    return load_model(r'mlModels/AutoEncoder/'+code), load_model(r'mlModels/Encoder/'+code)

def errorPercentage(model,data,comparison):
    model = model[0]
    comparison = [mean_squared_error(model.predict(np.array([x])), np.array([x])) for x in comparison]
    mse = mean_squared_error(model.predict(np.array([data])), np.array([data]))
    return len([x for x in comparison if x < mse]) / len(comparison)
d = {
    'product':'Blue Shells',
    'quantity':2000,
    'date':datetime.date(2019,12,31),
    'maturityDate':datetime.date(2025,1,1),
    'strikePrice':500,
    'underLyingPrice':318
}

#saveTrainData(normalizeData(loadData(normalized=False)),normalized=True)
#normalizeData(loadData(normalized=False))
#autoencoder,encoder =  loadModel(getModels()[-1])
#trainingData, testData = loadData(normalized=True,test=1000)
#trainModel(autoencoder,trainingData,5,512)
#saveModel(autoencoder,encoder)
#print(normalizeDatum(d))
#print(errorPercentage(loadModel(getModels()[-1]),normalizeDatum(d),testData))

#autoencoder.predict(np.array([testData[1]]))
#example = testData[71]
#printExample(example,autoencoder)
#print(encoder.predict(np.array([example])))
#q = list(example)
#q[5] += 0.5
#qms = mean_squared_error(autoencoder.predict(np.array([q])),np.array([q]))

#print(f"Avg {np.average(t)}, Std: {np.std(t)}, max {max(t)}, percentile: {len([x for x in t if x < qms]) / len(t)}")



#rintExample(q,autoencoder)
#print(encoder.predict(np.array([trainingData[70]])))
#print()




# retrieve the last layer of the autoencoder model
#decoder_layer = autoencoder.layers[-1]
# create the decoder model
#decoder = Model(encoded_input, decoder_layer(encoded_input))



'''
X = np.array(trainingData)
eps = 0.5
mins = 10
start = time.perf_counter()
clustering = DBSCAN(eps=eps, min_samples=mins).fit(X[:floor(len(trainingData)/1000)])
mins*=1000
print("Est time {}".format((time.perf_counter()-start)*100))
clusters = {x: len([y for y in clustering.labels_ if y == x]) for x in set(clustering.labels_)}
print(clusters)
print(len(clusters))
start = time.perf_counter()
clustering = DBSCAN(eps=eps, min_samples=mins).fit(X)
pickle.dump(clustering, open('trained.p','wb'))
print(time.perf_counter() - start)
'''
'''
pickle.dump(encoder, open('fenc.p','wb'))
pickle.dump(decoder, open('dec.p','wb'))
pickle.dump(autoencoder, open('aec.p','wb'))
pickle.dump(encoded, open('enc.p','wb'))
'''


