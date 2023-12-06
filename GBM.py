import numpy as np
import math
from scraper import StockInfo
import pandas as pd
import json
import matplotlib.pyplot as plt

def gbm(price, x, stdx, prob, years, simNum):
    # drift coefficent
    mu = 0.001
    # number of steps
    n = 100
    # volatility
    #sigma = np.std(x)
    sigma = stdx
    # calc each time step
    dt = years/n
    # simulation using numpy arrays
    St = np.exp(
        (mu - sigma ** 2 / 2) * dt
        + sigma * np.random.choice(x, p=prob, size=(simNum, n)).T
    )
    time = np.linspace(0,years,n + 1)
    # Require numpy array that is the same shape as St
    tt = np.full(shape=(simNum,n + 1), fill_value=time).T
    # include array of 1's
    St = np.vstack([np.ones(simNum), St])
    # multiply through by S0 and return the cumulative product of elements along a given simulation path (axis=0).
    St = price * St.cumprod(axis=0)
    
    return St, tt
    
def remap(x, oMin, oMax, nMin, nMax ):
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    reverseOutput = False   
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result

def weighted_avg_and_std(values, weights):
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))

def centerData(mean, data):
    data = data - mean
    return data

def make_GBM(ticker, years = 10, simNum = 10000):
    tick = StockInfo(ticker)
    f = open('valJSON.json')
    data = json.loads(json.loads(f.read()))

    data = data[ticker]
    price = tick.get_marketStockPrice()
    # make sure prob sum = 1
    prob = data["y"] / np.sum(data["y"])
    x = data["x"]
    # give x range [-1, 1], as we dont want multiplying by huge values
    x = np.array([-1 + 2 * (z - min(x)) / (max(x) - min(x)) for z in x])
    meanx, stdx = weighted_avg_and_std(x, prob)
    # centering values around 0
    x = x - meanx
    prices, time = gbm(price, x, stdx,prob, years, simNum)
        
    return prices
    
    
if __name__ == "__main__":
    prices = make_GBM("AAPL")
    gbm90 = []
    gbm10 = []
    meanGBM = []
    for i in range(len(prices)):
        gbm90.append(np.percentile(prices[i], 90))
        gbm10.append(np.percentile(prices[i], 10))
        meanGBM.append(np.percentile(prices[i], 75))

    plt.plot(meanGBM)
    plt.show()