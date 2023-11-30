import numpy as np

def createLinearTrend(start, stop, period):
    step = (stop - start) / period
    trend = np.arange(start, stop, step) / 100
    return trend


def createCyclicalTrend(start, stop, period):    
    trend = np.array([start, start / 2, stop / 2, stop])
    trend = np.resize(trend, period) / 100
    return trend
    

def createTrend(start, stop, period, trend):
    if trend == "cyclical":
        return createCyclicalTrend(start, stop, period)
    if trend == 'linear':
        return createLinearTrend(start, stop, period)
    
def createTrendAndDistribution(start, stop, period, trend, distribution, k = 100, target = "stop"):
    numberList = []
    if target == "stop":
        if distribution == 'normal':
            stop = np.random.normal(start, 2, k)
        elif distribution == 'uniform':
            stop = np.random.uniform(start - 1, start + 1, k)
        elif distribution == 'triangular':
            if start < stop:
                stop = np.random.triangular(start, np.mean([start, stop]), stop, k)
            else:
                stop = np.random.triangular(stop, stop + np.abs(start - stop), start, k)
        else:
            stop = [stop for i in range(k)]
        
        if trend == "cyclical":
            numberList = [createCyclicalTrend(start, x, period) for x in stop]
        if trend == 'linear':
            numberList = [createLinearTrend(start, x, period) for x in stop]
        #print(numberList[0])
    
    return numberList