import bs4 as bs
import pickle
import requests
import os
import pandas
import numpy as np
import random
import datetime
from sklearn.preprocessing import MinMaxScaler
from pandas.tseries.offsets import BDay
try:
    import quandl
except ImportError:
    pass

# GICS sector
# sector = ["Consumer Discretionary", "Consumer Staples", "Energy", "Financials", "Health Care", "Industrials",
#           "Information Technology", "Materials","Real Estate","Telecommunication Services","Utilities"]

def sp500_tickers(sector = "All"):

    if os.path.exists("ticker/sp500tickers_{}.pickle".format(sector)):
        with open("ticker/sp500tickers_{}.pickle".format(sector),"rb") as file:
            tickers = pickle.load(file)
    else:
        resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            if row.findAll('td')[3].text == sector or sector == "All":
                ticker = row.findAll('td')[0].text
                tickers.append(ticker)
        if tickers == []:
            print("Invalid sector !")
            exit()
        else:
            with open("ticker/sp500tickers_{}.pickle".format(sector),"wb") as file:
                pickle.dump(tickers,file)
    return tickers

def download_data(symbol):
    if not os.path.exists('./data/stock/{}.csv'.format(symbol)):
        df = quandl.get('WIKI/{}'.format(symbol).replace('.','_'), authtoken='x5eLEX_BwoVKBfXYWSLz')
        try:
            df.to_csv('./data/stock/{}.csv'.format(symbol))
            print('Imported from quandl: {}'.format(symbol))
            # record all the downloaded data tagged by period and mode
            # if os.path.exists("tickers_stocks.pickle"):
            #     with open("tickers_stocks.pickle","rb") as file:
            #         tickers = pickle.load(file)
            #     tickers.append(symbol)
            #     with open("tickers_stocks.pickle","wb") as file:
            #         pickle.dump(tickers,file)
            # else:
            #     with open("tickers_stocks.pickle","wb") as file:
            #         tickers = [symbol]
            #         pickle.dump(tickers,file)
        except IndexError:
            pass
    else:
        print('Data already exists:', symbol)

def download_tickers(tickers):
    for ticker in tickers:
        download_data(ticker)

def download_sp500():
    # download stocks from sp500
    tickers = sp500_tickers("All")
    for ticker in tickers:
        download_data(ticker)

def generate_list(sector, start, end):
    # generate a list of stocks which is available within a defined period
    with open("ticker/sp500tickers_{}.pickle".format(sector),'rb') as file:
        tickers = pickle.load(file)
    available_stock = []
    for symbol in tickers:
        print(symbol)
        if not os.path.exists('./data/stock/{}.csv'.format(symbol)):
            download_data(symbol)
        df = pandas.read_csv('./data/stock/{}.csv'.format(symbol), header=0, parse_dates=True, index_col=0)
        before_start = (datetime.datetime.strptime(start, '%Y-%m-%d') - BDay(200)).strftime('%Y-%m-%d')
        df = df[before_start : end]
        if df.empty:
            print("Historical data of {} does not cover period from {} to {}".format(symbol, start, end))
            continue
        elif df.index[0] != datetime.datetime.strptime(before_start,'%Y-%m-%d'):
            print("Historical data of {} does not cover period from {} to {}".format(symbol, start, end))
            continue
        available_stock.append(symbol)
    with open("ticker/sp500tickers_{}_{}_{}.pickle".format(sector, start, end),"wb") as file:
        pickle.dump(available_stock, file)

def generate_test_file(tickers, start, end):
    start = (datetime.datetime.strptime(start, '%Y-%m-%d') - BDay(200))
    end = datetime.datetime.strptime( end, "%Y-%m-%d")
    test_data = []

    for ticker in tickers:
        temp = pandas.read_csv('./data/stock/{}.csv'.format(ticker), header=0, parse_dates=True, index_col=0).loc[start:end]
        scaler = MinMaxScaler(feature_range=(0,1))
        temp['Scaled_adj_close'] = scaler.fit_transform(temp[['Adj. Close']])
        temp['Scaled_volume'] = scaler.fit_transform(temp[['Volume']])
        test_data.append(temp[['Open','High','Low','Close','Adj. Close','Volume','Scaled_adj_close','Scaled_volume']])
    print(test_data[0])

    for i in range(len(test_data[0])):
        temp = pandas.DataFrame(columns=['Open','High','Low','Close','Adj. Close','Volume','Scaled_adj_close','Scaled_volume'])
        for ii, ticker in enumerate(tickers):
            temp.loc[ii] = test_data[ii].iloc[i]
        temp.to_csv('./test/{}.csv'.format(test_data[0].index[i].strftime('%Y-%m-%d')))
        print('wrote',test_data[0].index[i].strftime('%Y-%m-%d'))





if __name__ == '__main__':

    # # group 1
    # sector = "Information Technology"
    # tickers = ['AAPL', 'AMAT', 'AMD', 'CSCO', 'EBAY', 'GLW', 'HPQ', 'IBM', 'INTC', 'KLAC', 'MSFT', 'MU', 'NVDA', 'QCOM', 'TXN']
    #
    # # group 2
    # sector = "Consumer Discretionary"
    # tickers = ['AZO', 'BBY', 'DHI', 'F', 'GPS', 'GRMN', 'HOG', 'JWN', 'MAT', 'MCD', 'NKE', 'SBUX', 'TJX', 'TWX', 'YUM']
    #
    # # group 3
    # sector = "Industrials"
    # tickers = ['BA', 'CAT', 'CTAS', 'EMR', 'FDX', 'GD', 'GE', 'LLL', 'LUV', 'MAS', 'MMM', 'NOC', 'RSG', 'UNP', 'WM']
    pass





