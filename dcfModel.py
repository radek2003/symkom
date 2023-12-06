import numpy as np


class DCF:
    def __init__(self, operatingMargin, revenueGrowthRate, taxRate, costOfCapital, 
                 salesToCapital, baseRevenue, forecastYears, terminalRevenueGrowthRate) -> None:
        self.operatingMargin = operatingMargin
        self.revenueGrowthRate = revenueGrowthRate
        self.costOfCapital = costOfCapital
        self.taxRate = taxRate
        self.forecastYears = forecastYears
        self.baseRevenue = baseRevenue
        self.salesToCapital = salesToCapital
        self.terminalYear = {"revenueGrowthRate" : terminalRevenueGrowthRate, "costOfCapital" : costOfCapital[-1]}
        
        self.cumulatedDiscountFactor = np.array([.0] * 10, dtype=float)
        self.OperatingIncomeForecast = np.array([.0] * 10, dtype=float)
        self.RevenueForecast = np.array([.0] * 10, dtype=float)
        self.EBITForecast = np.array([.0] * 10, dtype=float)
        self.ReinvestmentsForecast = np.array([.0] * 10, dtype=float)
        self.FCFF = np.array([.0] * 10, dtype=float)
        self.PV = np.array([.0] * 10, dtype=float)
    
    def make_cumulatedDiscountFactor(self):
        for i in range(self.forecastYears):
            if i == 0:
                self.cumulatedDiscountFactor[i] =  (1 / (1 + self.costOfCapital[i]))
                (1 / (1 + self.costOfCapital[i]))
                (self.cumulatedDiscountFactor[i])
            else:
                self.cumulatedDiscountFactor[i] =  self.cumulatedDiscountFactor[i - 1] * (1 / (1 + self.costOfCapital[i]))
            
        return self.cumulatedDiscountFactor
    
    def make_RevenueForecast(self):
        for i in range(self.forecastYears):
            if i == 0:
                self.RevenueForecast[i] = self.baseRevenue * (self.revenueGrowthRate[i] + 1)
            else:
                self.RevenueForecast[i] = self.RevenueForecast[i - 1] * (self.revenueGrowthRate[i] + 1)
        
        self.terminalYear["RevenueForecast"] = self.RevenueForecast[self.forecastYears - 2] * (self.revenueGrowthRate[self.forecastYears - 1] + 1)
        return self.RevenueForecast
    
    def make_OperatingIncomeForecast(self):
        if self.RevenueForecast[0] == 0:
            self.make_RevenueForecast()
        
        for i in range(self.forecastYears):
            self.OperatingIncomeForecast[i] = self.operatingMargin[i] * self.RevenueForecast[i]

        self.terminalYear["operatingMargin"] = self.operatingMargin[-1]
        self.terminalYear["OperatingIncomeForecast"] = self.terminalYear["operatingMargin"] * self.terminalYear["RevenueForecast"]
        return self.OperatingIncomeForecast
    
    def make_EBIT(self):
        if self.OperatingIncomeForecast[0] == 0:
            self.make_OperatingIncomeForecast()

        for i in range(self.forecastYears):
            self.EBITForecast[i] = self.OperatingIncomeForecast[i] * (1 - self.taxRate[i])
        
        self.terminalYear["EBIT"] = self.terminalYear["OperatingIncomeForecast"] * (1 - self.taxRate[-1])
        return self.EBITForecast
    
    def make_ReinvestmentsForecast(self):
        if self.RevenueForecast[0] == 0:
            self.make_RevenueForecast()

        for i in range(self.forecastYears):
            if i == 0:
                self.ReinvestmentsForecast[i] = (self.RevenueForecast[i] - self.baseRevenue) / self.salesToCapital[i]
            else:
                self.ReinvestmentsForecast[i] = (self.RevenueForecast[i] - self.RevenueForecast[i - 1]) / self.salesToCapital[i]
        
        self.terminalYear["ReinvestmentsForecast"] = (self.RevenueForecast[-1] - self.RevenueForecast[-2]) / self.salesToCapital[-1]
        return self.ReinvestmentsForecast
    
    def make_FCFF(self):
        if self.EBITForecast[0] == 0 or self.RevenueForecast[0] == 0:
            self.make_ReinvestmentsForecast()
            self.make_EBIT()

        for i in range(self.forecastYears):
            self.FCFF[i] = self.EBITForecast[i] - self.ReinvestmentsForecast[i]
        self.terminalYear["FCFF"] = self.terminalYear["EBIT"] - self.terminalYear["ReinvestmentsForecast"]

        self.terminalValue = self.terminalYear["FCFF"] / (self.terminalYear["costOfCapital"] - self.terminalYear["revenueGrowthRate"])
        return self.FCFF
    
    def make_PV(self):
        if self.FCFF[0] == 0:
            self.make_FCFF()

        if self.cumulatedDiscountFactor[0] == 0:
            self.make_cumulatedDiscountFactor()
        
        for i in range(self.forecastYears):
            self.PV[i] = self.FCFF[i] * self.cumulatedDiscountFactor[i]
        
        return self.PV
    
    def make_EquityValue(self):
        if self.FCFF[0] == 0:
            self.make_PV()
            
        equityValue = np.sum(self.PV) + (self.terminalValue * self.cumulatedDiscountFactor[-1])
        return equityValue