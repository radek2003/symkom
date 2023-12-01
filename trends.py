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
    
def createTrendAndDistribution(k, start, stop, period, trend, distribution, target = "stop"):
    numberList = []
    if target == "stop":
        if distribution == 'normal':
            stop = np.random.normal(np.mean([start, stop]), 5, k)
        elif distribution == 'uniform':
            stop = np.random.uniform(start, stop + start, k)
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
    
    return numberList