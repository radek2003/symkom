import numpy as np
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
from bs4 import BeautifulSoup
import requests
import regex as re
from multiprocessing.pool import ThreadPool
import random

class StockInfo:
    def __init__(self, symbol : str = ''):
        self.symbol = symbol
        self.current_price, self.week_change, self.half_year_change, self.year_change = '', '', '', ''
        self.soup_summary = ''
        self.soup_history = ''
        self.soup_financials = ''
        self.soup_balancesheet = ''
        self.headers_list = [
                        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
                        "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
                        "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
                        "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
                        ] 
        self.headers = {'User-Agent' : random.choice(self.headers_list) }
    
    def make_soup(self, url):
        r = requests.get(url, headers = self.headers, timeout=1000)
        soup = BeautifulSoup(r.content, "lxml")
        return soup  
    
    def make_many_soups(self):
        #self.soup_summary = self.make_soup(f'https://finance.yahoo.com/quote/{self.symbol}?p={self.symbol}')
        self.soup_financials = self.make_soup(f'https://finance.yahoo.com/quote/{self.symbol}/financials?p={self.symbol}')
        self.soup_cashflow = self.make_soup(f'https://finance.yahoo.com/quote/{self.symbol}/cash-flow?p={self.symbol}')
        self.soup_balancesheet = self.make_soup(f'https://finance.yahoo.com/quote/{self.symbol}/balance-sheet?p={self.symbol}')
    
    
    def get_ColumNames(self, soup):
        columNames = []
        rawColumNames = soup.find_all("div", {"class" : "D(tbhg)"})[0]
        rawColumNames = rawColumNames.find_all("span")
        for item in rawColumNames:
            columNames.append(item.text)
        
        return columNames
        
    def get_rowValues(self, columNames, soup):
        rawRow = soup.find_all("div", {"class" : "D(tbrg)"})[0]
        rawRow = rawRow.find_all("div", {"data-test" : "fin-row"})
        
        rowValues = []
        dictList = []
        for r, item in enumerate(rawRow):
            rowValues = item.find_all("span")
            
            cleanedRow = {}
            for c, val in enumerate(rowValues):
                cleanedRow[columNames[c]] = val.text
            dictList.append(cleanedRow)
        
        return dictList
    
    def get_FreeCashFlow(self):
        if not self.soup_cashflow:
            self.make_many_soups()
        try:
            columNames = self.get_ColumNames(self.soup_cashflow)
            dictList = self.get_rowValues(columNames, self.soup_cashflow)
        except IndexError:
            return 0

        return pd.json_normalize(dictList)
    
    def get_IncomeStatement(self):
        if not self.soup_financials:
            self.make_many_soups()
        try:
            columNames = self.get_ColumNames(self.soup_financials)
            dictList = self.get_rowValues(columNames, self.soup_financials)
        except IndexError:
            return 0

        return pd.json_normalize(dictList)
    
    def get_BalanceSheet(self):
        if not self.soup_balancesheet:
            self.make_many_soups()
        try:
            columNames = self.get_ColumNames(self.soup_balancesheet)
            dictList = self.get_rowValues(columNames, self.soup_balancesheet)
        except IndexError:
            return 0

        return pd.json_normalize(dictList)
    
    def get_historicalPrices(self):
        data = yf.download(self.symbol, start='2018-09-11')
        return data["Adj Close"].round(2)
        