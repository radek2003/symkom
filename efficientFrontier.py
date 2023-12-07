import pandas as pd
import json
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

def make_efficentFrontier(stock, weightsFilename = "weights"):
    mu = expected_returns.mean_historical_return(stock)
    S = risk_models.sample_cov(stock)
    ef = EfficientFrontier(mu, S)
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    ef.portfolio_performance(verbose=True)
    ef.save_weights_to_file(f"csv/{weightsFilename}.csv")
    
    return cleaned_weights
    

def get_efficentFrontier(forecastFilename, weightsFilename = "weights", percentage = 50):
    
    if "json" in forecastFilename:
        f = open('forecastFilename')
        data = json.loads(json.loads(f.read()))
        df = pd.DataFrame
        for ticker in data.keys():
            if ticker == "years" or ticker == "simNum":
                continue
            tempdf = pd.DataFrame.from_dict(data[ticker])
