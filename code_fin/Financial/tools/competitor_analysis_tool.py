import yfinance as yf
# from crewai_tools import tool
from crewai.tools import tool
@tool('competitor_analysis')
def competitor_analysis(ticker: str, num_competitors: int = 3):
    """
    Perform competitor analysis for a given stock.
    
    Args:
        ticker (str): The stock ticker symbol.
        num_competitors (int): Number of top competitors to analyze.
    
    Returns:
        dict: Competitor analysis results.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    sector = info.get('sector')
    industry = info.get('industry')
    
    # Get competitors in the same industry
    # industry_stocks = yf.Ticker(f"^{sector}").info.get('components', [])
    # competitors = [comp for comp in industry_stocks if comp != ticker][:num_competitors]
    tech_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'ADBE', 'INTC', 'CSCO',
                    'PYPL', 'CRM', 'AVGO', 'QCOM', 'TXN', 'AMD', 'NFLX', 'INTU', 'NOW', 'ORCL']
    industry_stocks=tech_tickers
    competitors=[comp for comp in industry_stocks if comp != ticker][:num_competitors]
    print(competitors)
    competitor_data = []
    for comp in competitors:
        comp_stock = yf.Ticker(comp)
        comp_info = comp_stock.info
        competitor_data.append({
            "ticker": comp,
            "name": comp_info.get('longName'),
            "market_cap": comp_info.get('marketCap'),
            "pe_ratio": comp_info.get('trailingPE'),
            "revenue_growth": comp_info.get('revenueGrowth'),
            "profit_margins": comp_info.get('profitMargins')
        })
    
    return {
        "main_stock": ticker,
        "industry": industry,
        "competitors": competitor_data
    }
