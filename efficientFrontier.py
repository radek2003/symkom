import pandas as pd
import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt
import json
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

#https://colab.research.google.com/drive/1ulDSw7DEJH1SYRVwvtJXYU0naFgaaBiR
def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns*weights )
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(1)
    return std, returns

def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate, table):
    results = np.zeros((3,num_portfolios))
    weights_record = []
    for i in range(num_portfolios):
        weights = np.random.random(len(table.columns))
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
        results[0,i] = portfolio_std_dev
        results[1,i] = portfolio_return
        results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
    return results, weights_record

def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
    return -(p_ret - risk_free_rate) / p_var

def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,1.0)
    bounds = tuple(bound for asset in range(num_assets))
    result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def portfolio_volatility(weights, mean_returns, cov_matrix):
    return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[0]

def min_variance(mean_returns, cov_matrix):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0, 1.0)
    bounds = tuple(bound for asset in range(num_assets))

    result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)

    return result

def efficient_return(mean_returns, cov_matrix, target):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)

    def portfolio_return(weights):
        return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[1]

    constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for asset in range(num_assets))
    result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return result


def efficient_frontier(mean_returns, cov_matrix, returns_range):
    efficients = []
    for ret in returns_range:
        efficients.append(efficient_return(mean_returns, cov_matrix, ret))
    return efficients

def display_calculated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate, table):
    results, _ = random_portfolios(num_portfolios,mean_returns, cov_matrix, risk_free_rate, table)
    
    max_sharpe = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
    #sdp, rp = portfolio_annualised_performance(max_sharpe['x'], mean_returns, cov_matrix)
    max_sharpe_allocation = pd.DataFrame(max_sharpe.x,index=table.columns,columns=['weight'])
    max_sharpe_allocation.weight = [round(i*100,2)for i in max_sharpe_allocation.weight]
    max_sharpe_allocation = max_sharpe_allocation.T
    
    min_vol = min_variance(mean_returns, cov_matrix)
    #sdp_min, rp_min = portfolio_annualised_performance(min_vol['x'], mean_returns, cov_matrix)
    min_vol_allocation = pd.DataFrame(min_vol.x,index=table.columns,columns=['weight'])
    min_vol_allocation.weight = [round(i*100,2)for i in min_vol_allocation.weight]
    min_vol_allocation = min_vol_allocation.T
    
    fig = plt.figure(figsize=(8, 5))
    plt.scatter(results[0,:],results[1,:],c=results[2,:], cmap='viridis', marker='o', s=8, alpha=1)
    plt.colorbar()
    plt.title('Calculated Portfolio Optimization based on Efficient Frontier')
    plt.xlabel('volatility')
    plt.ylabel('returns')
        
    return fig, min_vol_allocation, max_sharpe_allocation

def make_efficentFrontier(stock, weightsFilename = "weights"):
    mu = expected_returns.mean_historical_return(stock, frequency=12)
    S = risk_models.sample_cov(stock)
    ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.5))
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    #ef.portfolio_performance(verbose=True)
    #ef.save_weights_to_file(f"csv/{weightsFilename}.csv")
    
    return cleaned_weights
    
def make_ForecastDF(forecastFilename, percentage):
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
    

def get_efficentFrontierOPT(forecastFilename, weightsFilename = "weights", percentage = 50):
    if "json" in forecastFilename:
        df = make_ForecastDF(forecastFilename, percentage)
    else:
        df = pd.read_csv(forecastFilename)
    
    ef = make_efficentFrontier(df)
    return ef


def get_GraphefficentFrontier(forecastFilename, weightsFilename = "weights", percentage = 50):
    if "json" in forecastFilename:
        df = make_ForecastDF(forecastFilename, percentage)
    else:
        df = pd.read_csv(forecastFilename)
    
    returns = df.pct_change() 
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_portfolios = 5000
    risk_free_rate = 0
    fig, sharpe, vol = display_calculated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate, df)
    return fig, sharpe, vol