import numpy as np
import pandas as pd
import regex as re
from multiprocessing.pool import ThreadPool
import random
from scraper import StockInfo
from dcfModel import DCF, make_simpleValuation


ticker = "NVDA"

operatingMargin = np.array([35, 35, 37, 38, 39, 40, 40, 40, 40, 40, 40, 40]) / 100
RevenueGrowthRate = np.array([25, 25, 25, 25, 25, 25, 25, 25, 25, 5]) / 100
Costofcapital = np.array([12.21, 12.21, 12.21, 12.21, 12.21, 11.54, 10.86, 10.19, 9.52, 8.85]) / 100
salesToCapital = np.array([1.15, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15])
TaxRate = np.array([10, 10, 10, 10, 10, 10, 13, 16, 19, 22, 25, 25]) / 100
forecastYears = 10

valuation = make_simpleValuation(ticker, operatingMargin, RevenueGrowthRate, TaxRate, Costofcapital, salesToCapital, forecastYears)

print(valuation)