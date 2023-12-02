import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from stqdm import stqdm
import concurrent.futures
from dcfModel import DCF
from scraper import StockInfo
import trends


def make_simpleValuation(operatingMargin, revenueGrowthRate, taxRate, costOfCapital, 
                 salesToCapital, forecastYears, terminalRevenueGrowthRate, baseRevenue, debt, shares, cash):

    valuation = DCF(operatingMargin, revenueGrowthRate, taxRate, costOfCapital, salesToCapital, baseRevenue, forecastYears, terminalRevenueGrowthRate)
    EquityValue = valuation.make_EquityValue()
    stockPrice = (EquityValue + cash - debt) / shares
    
    return stockPrice


def get_valuationChecker(df, forecastYears):
    tickers = df["ticker"].to_list()

    for ticker in tickers:
        info = StockInfo(ticker)
        baseRevenue = info.get_BaseRevenue()
        debt = info.get_totalDebt()
        shares = info.get_shareCount()
        cash = info.get_FreeCash()
        tickerData = df[df["ticker"] == ticker]
        tickerData = tickerData.to_dict('records')[0]
        
        #,industry,,,operatingMarginDistribution,,
        # RevenueGrowthRateDistribution,,
        # ,CostofcapitalDistribution,salesToCapital,salesToCapitalDistribution,,
        # ,TaxRateEndDistribution

        terminalRevenueGrowthRate = tickerData['RevenueGrowthRateTerminalValue'] / 100 # może być średnia z przemysłu
        operatingMargin = trends.createTrend(tickerData['operatingMarginStart'], tickerData['operatingMarginTarget'], 
                                                forecastYears, tickerData['operatingMarginGrowthTrend'])
        
        revenueGrowthRate = trends.createTrend(tickerData['RevenueGrowthRateStart'], tickerData['RevenueGrowthRateEnd'], 
                                                forecastYears, tickerData['RevenueGrowthRateGrowthTrend'])
        costOfCapital = trends.createTrend(tickerData['CostofcapitalStart'], tickerData['CostofcapitalEnd'], 
                                           forecastYears, tickerData['CostofcapitalTrend'])
        taxRate = trends.createTrend(tickerData['TaxRateStart'], tickerData['TaxRateEnd'], forecastYears, 'linear' )
        salesToCapital = trends.createTrend(1.5, 1.51, forecastYears, 'linear' ) * 100

        valuation = make_simpleValuation(operatingMargin, revenueGrowthRate, taxRate, costOfCapital, salesToCapital, forecastYears, 
                                terminalRevenueGrowthRate, baseRevenue, debt, shares, cash)
        
        print(operatingMargin)
        print(revenueGrowthRate)
        print(taxRate)
        print(costOfCapital)
        print(salesToCapital)
        print(valuation)

def get_valuationDistribution(df, tickers, forecastYears, k = 1000):
    for ticker in stqdm(tickers):
        info = StockInfo(ticker)
        baseRevenue = info.get_BaseRevenue()
        debt = info.get_totalDebt()
        shares = info.get_shareCount()
        cash = info.get_FreeCash()
        tickerData = df[df["ticker"] == ticker]
        tickerData = tickerData.to_dict('records')[0]
        
        #,industry,salesToCapital,salesToCapitalDistribution,,

        terminalRevenueGrowthRate = tickerData['RevenueGrowthRateTerminalValue'] / 100 # może być średnia z przemysłu
        operatingMargin = trends.createTrendAndDistribution(k, tickerData['operatingMarginStart'], tickerData['operatingMarginTarget'], 
                                                forecastYears, tickerData['operatingMarginGrowthTrend'], tickerData['operatingMarginDistribution'])
        revenueGrowthRate = trends.createTrendAndDistribution(k, tickerData['RevenueGrowthRateStart'], tickerData['RevenueGrowthRateEnd'], 
                                                forecastYears, tickerData['RevenueGrowthRateGrowthTrend'], tickerData['RevenueGrowthRateDistribution'])
        costOfCapital = trends.createTrendAndDistribution(k, tickerData['CostofcapitalStart'], tickerData['CostofcapitalEnd'], 
                                           forecastYears, tickerData['CostofcapitalTrend'], tickerData['CostofcapitalDistribution'])
        taxRate = trends.createTrendAndDistribution(k, tickerData['TaxRateStart'], tickerData['TaxRateEnd'], 
                                                    forecastYears, 'linear', "")
        #tickerData['TaxRateEndDistribution']
        salesToCapital = trends.createTrendAndDistribution(k, 1.5, 1.51, forecastYears, 'linear', '')
        valuationDensity = []
        with concurrent.futures.ProcessPoolExecutor() as executor:            
            future_to_val = {executor.submit(make_simpleValuation, operatingMargin[i], revenueGrowthRate[i], taxRate[i], 
                                             costOfCapital[i], salesToCapital[i] * 100, forecastYears, terminalRevenueGrowthRate, 
                                             baseRevenue, debt, shares, cash): i for i in range(len(operatingMargin))}
            for future in concurrent.futures.as_completed(future_to_val):
                url = future_to_val[future]
                data = future.result()
                valuationDensity.append(data)
            
        print(operatingMargin[-1])
        print(revenueGrowthRate[-1])
        print(taxRate[-1])
        print(costOfCapital[-1])
        print(salesToCapital[-1])
        
    return valuationDensity


# https://numpy.org/doc/1.16/reference/routines.random.html
if __name__ == "__main__":
    forecastYears = 10
    df = pd.read_csv('csv/tickers.csv')
    get_valuationChecker(df, 10)
