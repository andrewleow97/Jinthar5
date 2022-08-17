import pandas as pd
from .models import Portfolio
import yfinance as yf
import json
import pandas as pd
from flask import Flask, request, jsonify
from App import db

def getDf():
    df = pd.DataFrame([stocks.json() for stocks in Portfolio.query.all()])

def stockInfo(ticker):
    #obtains information of a single stock
    stockData = yf.Ticker(ticker)
    if stockData.info['regularMarketPrice'] == None:
        return "Invalid Stock ticker"
    else:
        stockDictionary = {
            "symbol":stockData.info['symbol'],
            "name":stockData.info['shortName'],
            "currentPrice":stockData.info['regularMarketPrice'],
            "dayHigh":stockData.info['dayHigh'],
            "dayLow":stockData.info['dayLow'],
        }
    return json.dumps(stockDictionary)

def getAllPorfolio():
    return jsonify({"Portfolio":[stocks.json() for stocks in Portfolio.query.all()]}), 200

def getUserPortfolio(Country):
    return jsonify({"Portfolio":[stocks.json() for stocks in Portfolio.query.filter_by(Country=Country.upper())]}), 200

def populatePortfolioInfo(portfolios):
    # obtains stock information for all the stocks in the list
    ###  change to retrieve data from sql!
    portfolio = {}
    tickers = yf.Tickers(" ".join(portfolios))

    for stockTicker, stockInfo in tickers.tickers.items():
        portfolio[stockTicker] = {
            "name":stockInfo.info['shortName'],
            "currentPrice":float(round(stockInfo.info['regularMarketPrice']),2),
            "dailyPnL": round((stockInfo.info["regularMarketPrice"] - stockInfo.info["previousClose"]),2),
            "dailyPnLPercentage": round(((stockInfo.info["regularMarketPrice"] - stockInfo.info["previousClose"]) / stockInfo.info["previousClose"])*100,2),
            "country": (stockInfo.info["currency"])
        }
    print("retrieval from yfinance completed")  
    return portfolio

def retrieveStockUpdates(df):
    tickers = list(set(df['Ticker']))
    updatedPortfolioInfo = populatePortfolioInfo(tickers)
    df['Name'] = df["Ticker"].apply(lambda x : updatedPortfolioInfo[x.upper()]["name"])
    df['MarketValue'] = df["Ticker"].apply(lambda x : updatedPortfolioInfo[x.upper()]["currentPrice"])
    df['country'] = df["Ticker"].apply(lambda x : updatedPortfolioInfo[x.upper()]["country"])
    df['DailyPnL'] = df["Ticker"].apply(lambda x : updatedPortfolioInfo[x.upper()]["dailyPnL"])
    df['DailyPnLPercentage'] = df["Ticker"].apply(lambda x : updatedPortfolioInfo[x.upper()]["dailyPnLPercentage"])
    df['UnrealisedPnL'] = (df['MarketValue'] - df['Price']) * df['Quantity']
    df['UnrealisedPnLPercentage'] = round(((df['MarketValue']-df['Price'])/df['Price'])*100,2)
    return df
    
def getDf():
    df = pd.DataFrame([stocks.json() for stocks in Portfolio.query.all()])

def newTickerInfo(ticker, quantity, price):
    stockData = yf.Ticker(ticker)

    if stockData.info['regularMarketPrice'] == None:
        return "Invalid Stock ticker"
    else:
        newTicker = {
            "Ticker": stockData.info['symbol'], 
            "Quantity": quantity, 
            "Price": price,
            "Name": stockData.info['shortName'],
            "Country": stockData.info['currency'],
            "MarketValue": round(stockData.info['regularMarketPrice'],2),
            "UnrealisedPnL": round(((stockData.info['regularMarketPrice']-price) * quantity),2),
            "UnrealisedPnLPercentage": round(((stockData.info['regularMarketPrice']-price)/price)*100,2),
            "dailyPnL": round((stockData.info["regularMarketPrice"] - stockData.info["previousClose"]),2),
            "dailyPnLPercentage": round(((stockData.info["regularMarketPrice"] - stockData.info["previousClose"]) / stockData.info["previousClose"])*100,2)
        }
        return newTicker

def addStock(ticker, quantity, price, country):
    if country.upper() == "SGD":
        ticker += ".si"
    newStock = newTickerInfo(ticker, quantity, price)
    if newStock == "Invalid Stock ticker":
        return newStock
    else:
        print(newStock)
        portfolioObject = Portfolio(
            Ticker = newStock['Ticker'], 
            Quantity = newStock['Quantity'],
            Price = newStock['Price'], 
            Name = newStock['Name'], 
            Country = newStock['Country'], 
            MarketValue = newStock['MarketValue'], 
            DailyPnL = newStock['dailyPnL'], 
            DailyPnLPercentage = newStock['dailyPnLPercentage'], 
            UnrealisedPnL = newStock['UnrealisedPnL'], 
            UnrealisedPnLPercentage = newStock['UnrealisedPnLPercentage']
            )
        db.session.add(portfolioObject)
        db.session.commit()
        
    return "success"