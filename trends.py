import numpy as np

def createLinearTrend(start, stop, period):
    if stop - start == 0:
        stop += 0.0001
    step = (stop - start) / period
    trend = np.arange(start, stop, step) / 100
    return trend


def createCyclicalTrend(start, stop, period):
    if stop - start == 0:
        stop += 0.0001
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
            stop = np.random.normal(stop, stop * 0.2, k)
        elif distribution == 'uniform':
            stop = np.random.uniform(stop - stop * 0.2, stop + stop * 0.2, k)

        elif distribution == 'triangular':
                stop = np.random.triangular(stop - stop * 0.2, stop, stop + stop * 0.2, k)
        else:
            stop = [stop for i in range(k)]
        
        if trend == "cyclical":
            numberList = [createCyclicalTrend(start, x, period) for x in stop]
        if trend == 'linear':
            numberList = [createLinearTrend(start, x, period) for x in stop]
    
    return numberList