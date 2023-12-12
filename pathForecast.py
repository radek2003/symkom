import numpy as np
import math
from scraper import StockInfo
import pandas as pd
import json
import matplotlib.pyplot as plt

#http://www.columbia.edu/~ks20/FE-Notes/4700-07-Notes-GBM.pdf
def gbm(price, x, stdx, prob, years, simNum):
    # drift coefficent - how fast path price moves
    mu = 0.05
    # number of steps
    n = 12 * years
    # volatility
    sigma = 0.15
    # calc each time step
    dt = years/n
    # simulation using numpy arrays
    St = np.exp(
        (mu - sigma ** 2 / 2) * dt
        + sigma * np.random.choice(x, p=prob, size=(simNum, n)).T
    )
    time = np.linspace(0, years, n + 1)
    # Require numpy array that is the same shape as St
    tt = np.full(shape=(simNum, n + 1), fill_value=time).T
    # include array of 1's
    St = np.vstack([np.ones(simNum), St])
    # multiply through by S0 and return the cumulative product of elements along a given simulation path (axis=0).
    St = price * St.cumprod(axis=0)
    return St, time

def universalModel(price, x, prob, years, simNum):
    results = []
    volatility = 0.5
    drift = 0.2
    months = 12 * years + 1
    for i in range(simNum):
        basic = np.array([price] * months)
        rand = np.random.choice(x, p=prob, size = months)
        for time in range(1, months):
            basic[time] = (basic[time - 1] * np.exp((1 + volatility ) * time / (drift * 10000)) + (rand[time] - basic[time - 1]) * volatility)
        
        results.append(basic)
    
    results = np.matrix(results).T
    time = np.linspace(0, years, months)
    return results, time
    
def weighted_avg_and_std(values, weights):
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))


def make_GBM(data ,ticker, years = 10, simNum = 10000):
    tick = StockInfo(ticker)
    data = data[ticker]
    price = tick.get_marketStockPrice()
    # make sure prob sum = 1
    prob = data["y"] / np.sum(data["y"])
    x = np.array(data["x"])
    meanx, stdx = weighted_avg_and_std(x, prob)
    # center returns around 0
    x-= meanx
    x /= stdx
    prices, time = gbm(price, x, stdx,prob, years, simNum)
        
    return prices, time

def make_universal(data ,ticker, years = 10, simNum = 10000):
    tick = StockInfo(ticker)
    data = data[ticker]
    price = tick.get_marketStockPrice()
    prob = data["y"] / np.sum(data["y"])
    prices, time = universalModel(price, data["x"], prob, years, simNum)
        
    return prices, time
    
    
def unpackSimulation(ticker, prices, time, pricesDict):
    gbm50 = []
    gbm60 = []
    gbm75 = []
    gbm25 = []
    prices = np.array(prices)
    for i in range(len(prices[0:,:])):
        gbm50.append(np.round(np.percentile(prices[i, :], 50), 2))
        gbm75.append(np.round(np.percentile(prices[i, :], 75), 2))
        gbm60.append(np.round(np.percentile(prices[i, :], 60), 2))
        gbm25.append(np.round(np.percentile(prices[i, :], 25), 2))
        
    pricesDict[ticker] = {
        "gbm25" : gbm25,
        "gbm50": gbm50,
        "gbm60" : gbm60,
        "gbm75" : gbm75,
        "time" : np.round(time, 2).tolist(),
    }
    
    return pricesDict

def forecastGBMAllPaths(years = 10, simNum = 1000):
    f = open('jsons/valJSON.json')
    data = json.loads(json.loads(f.read()))
    pricesDict = {"years" : years, "simNum" : simNum}
    for ticker in data.keys():
        prices, time = make_GBM(data, ticker, years, simNum = simNum)            
        pricesDict = unpackSimulation(ticker, prices, time, pricesDict)

    pricesDict = json.dumps(pricesDict)
    with open('jsons/gbmForecast.json', 'w') as f:
        json.dump(pricesDict, f, ensure_ascii=False, indent=2)
        
def forecastUniversalAllPaths(years = 10, simNum = 1000):
    f = open('jsons/valJSON.json')
    data = json.loads(json.loads(f.read()))
    pricesDict = {"years" : years, "simNum" : simNum}
    for ticker in data.keys():
        prices, time = make_universal(data, ticker, years, simNum = simNum)            
        pricesDict = unpackSimulation(ticker, prices, time, pricesDict)

    pricesDict = json.dumps(pricesDict)
    with open('jsons/universalForecast.json', 'w') as f:
        json.dump(pricesDict, f, ensure_ascii=False, indent=2)
 
if __name__ == "__main__":
    forecastGBMAllPaths()
    forecastUniversalAllPaths()