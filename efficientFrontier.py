import pandas as pd
import json
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

def make_efficentFrontier(stock, weightsFilename = "weights"):
    mu = expected_returns.mean_historical_return(stock, frequency=12)
    S = risk_models.sample_cov(stock)
    ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.5))
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    ef.portfolio_performance(verbose=True)
    ef.save_weights_to_file(f"csv/{weightsFilename}.csv")
    
    return cleaned_weights
    
def make_GBMForecastDF(forecastFilename, percentage):
    f = open(forecastFilename)
    data = json.loads(json.loads(f.read()))
    df = pd.DataFrame()
    i = 0
    for ticker in data.keys():
        if ticker == "years" or ticker == "simNum":
            continue
        if i == 0:
            df = pd.DataFrame.from_dict(data[ticker][f"gbm{percentage}"])
            df.rename(columns = {0:ticker}, inplace = True)
        else:
            tempdf = pd.DataFrame.from_dict(data[ticker]["gbm50"])
            tempdf.rename(columns = {0:ticker}, inplace = True)
            df = pd.concat([df, tempdf], axis=1)
        i +=1
        
    return df
    

def get_efficentFrontier(forecastFilename, weightsFilename = "weights", percentage = 50):
    if "json" in forecastFilename:
        df = make_GBMForecastDF(forecastFilename, percentage)
    else:
        df = pd.read_csv(forecastFilename)
    
    return df

df = get_efficentFrontier("jsons/gbmForecast.json")
print(make_efficentFrontier(df, weightsFilename = "weights"))