import yfinance as yf

ticker='AAPL'
benchmark= "^GSPC"
period = "1y"

stock = yf.Ticker(ticker)
benchmark_index = yf.Ticker(benchmark)

# stock_data = stock.history(period=period)['Close']
# benchmark_data = benchmark_index.history(period=period)['Close']
# print(stock_data)
# print(benchmark_data)

info = stock.info
print(1)
sector = info.get('sector')
print(sector)
industry = info.get('industry')
print(industry)

# Get competitors in the same industry
# industry_stocks = yf.Sector(f"^{sector}").info.get('components', [])
#
# import yfinance as yf
#

# 获取特定板块的所有股票
def get_tickers_by_sector(sector):
    # 由于yfinance本身不直接支持按板块获取股票，我们需要使用另一种方式
    # 比如先获取所有股票的信息，然后筛选
    tickers = yf.Tickers('AAPL MSFT AMZN GOOGL')  # 示例：列出一些股票
    filtered_tickers = [ticker for ticker in tickers.tickers if tickers.tickers[ticker].info.get('sector', '') == sector]
    return filtered_tickers


# 示例：获取所有"Technology"板块的股票
# sector = 'Technology'
# tickers = get_tickers_by_sector(sector)
# print(tickers)
industry_stocks=get_tickers_by_sector(sector)
competitors = [comp for comp in industry_stocks if comp != ticker][:4]


# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP

# ECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# ERROR:yfinance:404 Client Error: Not Found for url: https://query2.finance.yahoo.com/v10/finance/quoteSummary/%5ETECHNOLOGY?modules=financialData%2CquoteType%2CdefaultKeyStatistics%2CassetProfile%2CsummaryDetail&corsDomain=finance.yahoo.com&formatted=false&symbol=%5ETECHNOLOGY&crumb=IScfmGeLlHP
# # **Comprehensive Investment Strategy for Apple Inc. (AAPL)**