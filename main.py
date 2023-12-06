import numpy as np
import pandas as pd
from stqdm import stqdm
import concurrent.futures
import json

from dcfModel import DCF
from scraper import StockInfo
import trends


def make_simpleValuation(operatingMargin, revenueGrowthRate, taxRate, costOfCapital, 
                 salesToCapital, forecastYears, terminalRevenueGrowthRate, baseRevenue, debt, shares, cash):

    valuation = DCF(operatingMargin, revenueGrowthRate, taxRate, costOfCapital, salesToCapital, baseRevenue, forecastYears, terminalRevenueGrowthRate)
    EquityValue = valuation.make_EquityValue()
    stockPrice = (EquityValue + cash - debt) / shares
    
    return stockPrice


def get_valuationChecker(df, tickers, forecastYears):
    for ticker in tickers:
        info = StockInfo(ticker)
        baseRevenue = info.get_BaseRevenue()
        debt = info.get_totalDebt()
        shares = info.get_shareCount()
        cash = info.get_FreeCash()
        tickerData = df[df["ticker"] == ticker]
        tickerData = tickerData.to_dict('records')[0]

        terminalRevenueGrowthRate = tickerData['RevenueGrowthRateTerminalValue'] / 100 # może być średnia z przemysłu
        operatingMargin = trends.createTrend(tickerData['operatingMarginStart'], tickerData['operatingMarginTarget'], 
                                                forecastYears, tickerData['operatingMarginGrowthTrend'])
        
        revenueGrowthRate = trends.createTrend(tickerData['RevenueGrowthRateStart'], tickerData['RevenueGrowthRateEnd'], 
                                                forecastYears, tickerData['RevenueGrowthRateGrowthTrend'])
        costOfCapital = trends.createTrend(tickerData['CostofcapitalStart'], tickerData['CostofcapitalEnd'], 
                                           forecastYears, tickerData['CostofcapitalTrend'])
        taxRate = trends.createTrend(tickerData['TaxRateStart'], tickerData['TaxRateEnd'], forecastYears, 'linear' )
        salesToCapital = trends.createTrend(tickerData['salesToCapital'], tickerData['salesToCapital'], forecastYears, 'linear')

        valuation = make_simpleValuation(operatingMargin, revenueGrowthRate, taxRate, costOfCapital, salesToCapital * 100, forecastYears, 
                                terminalRevenueGrowthRate, baseRevenue, debt, shares, cash)
        
        print(operatingMargin)
        print(revenueGrowthRate)
        print(taxRate)
        print(costOfCapital)
        print(salesToCapital)
        print(valuation)

def get_valuationDistribution(df, tickers, forecastYears, k = 1000):
    dictList = {}
    for ticker in stqdm(tickers):
        info = StockInfo(ticker)
        baseRevenue = info.get_BaseRevenue()
        debt = info.get_totalDebt()
        shares = info.get_shareCount()
        cash = info.get_FreeCash()
        tickerData = df[df["ticker"] == ticker]
        tickerData = tickerData.to_dict('records')[0]
        
        terminalRevenueGrowthRate = tickerData['RevenueGrowthRateTerminalValue'] / 100
        operatingMargin = trends.createTrendAndDistribution(k, tickerData['operatingMarginStart'], tickerData['operatingMarginTarget'], 
                                                forecastYears, tickerData['operatingMarginGrowthTrend'], tickerData['operatingMarginDistribution'])
        revenueGrowthRate = trends.createTrendAndDistribution(k, tickerData['RevenueGrowthRateStart'], tickerData['RevenueGrowthRateEnd'], 
                                                forecastYears, tickerData['RevenueGrowthRateGrowthTrend'], tickerData['RevenueGrowthRateDistribution'])
        costOfCapital = trends.createTrendAndDistribution(k, tickerData['CostofcapitalStart'], tickerData['CostofcapitalEnd'], 
                                           forecastYears, tickerData['CostofcapitalTrend'], tickerData['CostofcapitalDistribution'])
        taxRate = trends.createTrendAndDistribution(k, tickerData['TaxRateStart'], tickerData['TaxRateEnd'], 
                                                    forecastYears, 'linear', tickerData['TaxRateEndDistribution'])
        salesToCapital = trends.createTrendAndDistribution(k, tickerData['salesToCapital'], tickerData['salesToCapital'], forecastYears, 'linear', '')
        valuationDensity = []
        with concurrent.futures.ProcessPoolExecutor() as executor:            
            future_to_val = {executor.submit(make_simpleValuation, operatingMargin[i], revenueGrowthRate[i], taxRate[i], 
                                             costOfCapital[i], salesToCapital[i] * 100, forecastYears, terminalRevenueGrowthRate, 
                                             baseRevenue, debt, shares, cash): i for i in stqdm(range(len(operatingMargin)))}
            for future in concurrent.futures.as_completed(future_to_val):
                data = future.result()
                if data > 0:
                    valuationDensity.append(data)
        
        valuationDensity = list(np.histogram(valuationDensity, density=True, bins = int(np.ceil(np.sqrt(k)))))
        
        valuationDensity[0] = valuationDensity[0] / np.sum(valuationDensity[0])
        valuationDensity = [valuationDensity[0], 0.5*(valuationDensity[1][1:]+valuationDensity[1][:-1])]
        dictList[ticker] = {
                "x" : list(valuationDensity[1]),
                "y" : list(valuationDensity[0])}
        
    valJSON = json.dumps(dictList)
    with open('valJSON.json', 'w') as f:
        json.dump(valJSON, f, ensure_ascii=False, indent=2)
        
    return valuationDensity


if __name__ == "__main__":
    forecastYears = 10
    df = pd.read_csv('csv/tickers.csv')
    get_valuationChecker(df, ["NVDA"], 10)
