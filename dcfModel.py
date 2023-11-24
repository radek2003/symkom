import numpy as np
from scraper import StockInfo


class DCF:
    def __init__(self, operatingMargin, RevenueGrowthRate, TaxRate, Costofcapital, 
                 salesToCapital, baseRevenue, forecastYears = 10) -> None:
        self.operatingMargin = operatingMargin
        self.RevenueGrowthRate = RevenueGrowthRate
        self.Costofcapital = Costofcapital
        self.TaxRate = TaxRate
        self.forecastYears = forecastYears
        self.baseRevenue = baseRevenue
        self.salesToCapital = salesToCapital
        self.terminalYear = {"RevenueGrowthRate" : RevenueGrowthRate[-1], "Costofcapital" : Costofcapital[-1]}
        
        self.CumulatedDiscountFactor = np.array([])
        self.OperatingIncomeForecast = np.array([])
        self.RevenueForecast = np.array([])
        self.EBITForecast = np.array([])
        self.ReinvestmentsForecast = np.array([])
        self.FCFF = np.array([])
        self.PV = np.array([])
    
    def make_CumulatedDiscountFactor(self):
        for i in range(self.forecastYears):
            if i == 0:
                self.CumulatedDiscountFactor = np.append(self.CumulatedDiscountFactor, 1 / (1 + self.Costofcapital[i]))
            else:
                self.CumulatedDiscountFactor = np.append(self.CumulatedDiscountFactor, self.CumulatedDiscountFactor[i - 1] * (1 / (1 + self.Costofcapital[i])))
                
        return self.CumulatedDiscountFactor
    
    def make_RevenueForecast(self):
        for i in range(self.forecastYears):
            if i == 0:
                self.RevenueForecast = np.append(self.RevenueForecast, self.baseRevenue * (self.RevenueGrowthRate[i] + 1))
            else:
                self.RevenueForecast = np.append(self.RevenueForecast, self.RevenueForecast[i - 1] * (self.RevenueGrowthRate[i] + 1))
        
        self.terminalYear["RevenueForecast"] = self.RevenueForecast[self.forecastYears - 2] * (self.RevenueGrowthRate[self.forecastYears - 1] + 1)
        return self.RevenueForecast
    
    def make_OperatingIncomeForecast(self):
        if self.RevenueForecast.size <= 0:
            self.make_RevenueForecast()
        
        for i in range(self.forecastYears):
            self.OperatingIncomeForecast = np.append(self.OperatingIncomeForecast, self.operatingMargin[i] * self.RevenueForecast[i])

        self.terminalYear["operatingMargin"] = self.operatingMargin[-1]
        self.terminalYear["OperatingIncomeForecast"] = self.terminalYear["operatingMargin"] * self.terminalYear["RevenueForecast"]
        return self.OperatingIncomeForecast
    
    def make_EBIT(self):
        if self.OperatingIncomeForecast.size <= 0:
            self.make_OperatingIncomeForecast()

        for i in range(self.forecastYears):
            self.EBITForecast = np.append(self.EBITForecast, self.OperatingIncomeForecast[i] * (1 - self.TaxRate[i]))    
        
        self.terminalYear["EBIT"] = self.terminalYear["OperatingIncomeForecast"] * (1 - self.TaxRate[-1])
        return self.EBITForecast
    
    def make_ReinvestmentsForecast(self):
        if self.RevenueForecast.size <= 0:
            self.make_RevenueForecast()

        for i in range(self.forecastYears):
            if i == 0:
                self.ReinvestmentsForecast = np.append(self.ReinvestmentsForecast, (self.RevenueForecast[i] - self.baseRevenue) / self.salesToCapital[i])   
            else:
                self.ReinvestmentsForecast = np.append(self.ReinvestmentsForecast, (self.RevenueForecast[i] - self.RevenueForecast[i - 1]) / self.salesToCapital[i]) 
        
        self.terminalYear["ReinvestmentsForecast"] = (self.RevenueForecast[-1] - self.RevenueForecast[-2]) / self.salesToCapital[-1]
        return self.ReinvestmentsForecast
    
    def make_FCFF(self):
        if self.EBITForecast.size <= 0 or self.RevenueForecast.size <= 0:
            self.make_ReinvestmentsForecast()
            self.make_EBIT()
            
        for i in range(self.forecastYears):
            self.FCFF = np.append(self.FCFF, self.EBITForecast[i] - self.ReinvestmentsForecast[i])
        self.terminalYear["FCFF"] = self.terminalYear["EBIT"] - self.terminalYear["ReinvestmentsForecast"]
        
        self.terminalValue = self.terminalYear["FCFF"] / (self.terminalYear["Costofcapital"] - self.terminalYear["RevenueGrowthRate"])
        return self.FCFF
    
    def make_PV(self):
        if self.FCFF.size <= 0 or self.CumulatedDiscountFactor.size <= 0:
            self.make_FCFF()
            self.make_CumulatedDiscountFactor()
        
        for i in range(self.forecastYears):
            self.PV = np.append(self.PV, self.FCFF[i] * self.CumulatedDiscountFactor[i])

        return self.PV
    
    def make_EquityValue(self):
        if self.FCFF.size <= 0:
            self.make_PV()
        
        equityValue = np.sum(self.PV) + (self.terminalValue * self.CumulatedDiscountFactor[-1])
        return equityValue
    

def make_simpleValuation(ticker, operatingMargin, RevenueGrowthRate, TaxRate, Costofcapital, 
                 salesToCapital, forecastYears):
    
    info = StockInfo(ticker)
    baseRevenue = info.get_BaseRevenue()
    debt = info.get_totalDebt()
    shares = info.get_shareCount()
    cash = info.get_FreeCash()
    
    valuation = DCF(operatingMargin, RevenueGrowthRate, TaxRate, Costofcapital, salesToCapital, baseRevenue, forecastYears)
    EquityValue = valuation.make_EquityValue()
    
    stockPrice = (EquityValue + cash - debt) / shares

    return stockPrice