import streamlit as st
from code_fin.OpenAladdin.open_aladdin.main import (
    fetch_stock_data,
    AdvancedRealTimeRiskAssessment,
)
import time
import pandas as pd
st.set_page_config(page_title="金融综合风险评估Agent", page_icon="👨📈")

st.title("金融综合风险评估Agent")
# st.caption("This app allows you to compare the performance of two stocks and generate detailed reports.")
st.markdown("""
    这款 Agent是一款风险分析和投资组合管理Agent，灵感来自BlackRock的 Aladdin 平台，旨在为股票、证券和其他市场工具提供全面的风险评估和管理工具。
## 特征

- **综合风险分析**：评估股票、债券、衍生品等多种金融工具的风险。
- **实时数据处理**：根据市场变化不断更新风险评估。
- **先进的机器学习模型**：利用最先进的 ML 算法进行预测分析和风险预测。
- **可定制的风险指标**：计算和跟踪各种风险指标，包括 VaR、预期缺口和自定义指标。
- **投资组合优化**：根据风险回报状况构建和重新平衡投资组合的工具。

""")

openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))


# User input
stock_symbol = st.text_input("输入股票、证券代码类别，“,”分割开 (e.g., AAPL,GOOGL,MSFT,AMZN):", "AAPL,GOOGL,MSFT,AMZN")



def run_analysis(stock_symbol):
    tickers=stock_symbol.split(',')
    # tickers = [
    #     "AAPL",
    #     "GOOGL",
    #     "MSFT",
    #     "AMZN",
    #     "^GSPC",
    # ]  # Including S&P 500 for market returns
    historical_data = {
        ticker: fetch_stock_data(ticker) for ticker in tickers
    }

    risk_assessor = AdvancedRealTimeRiskAssessment(historical_data)
    risk_assessor.start_continuous_training()

    try:
        # Run for a while to allow some training iterations
        time.sleep(10)

        # Perform risk assessment
        risk_results = risk_assessor.run_risk_assessment(
            forecast_horizon=4
        )  # 1-year forecast

        # Output results
        # risk_assessor.output_results(risk_results, "json")
        # risk_assessor.output_results(risk_results, "csv")

        # risk_measures = {
        #     "Current_Volatility": float(predicted_volatility[-1]),
        #     "Value_at_Risk": var,
        #     "Expected_Shortfall": es,
        #     "Beta": beta,
        #     "Sharpe_Ratio": sharpe_ratio,
        #     "Sortino_Ratio": sortino_ratio,
        #     "Max_Drawdown": max_drawdown,
        #     "Long_Term_Volatility_Forecast": long_term_forecast,
        # }
        # Print some results
        # MSFT 的风险评估：

        stocknames=[]
        values = {
            'Current_Volatility': [],
            'Value_at_Risk': [],
            'Expected_Shortfall': [],
            'Beta': [],
            'Sharpe_Ratio': [],
            'Sortino_Ratio': [],
            'Max_Drawdown': [],
            'Long_Term_Volatility_Forecast': []
        }
        for ticker, measures in risk_results.items():
            print(f"\nRisk Assessment for {ticker}:")
            stocknames.append(ticker)
            for measure, value in measures.items():
                vs=values.get(measure)

                if isinstance(value, list):

                    ts=[float(f"{v:.5f}") for v in value[:5]]
                    vs.append( f"{ts[:5]}")
                    print(
                        f"{measure}: [showing first 5 values] {value[:5]}"
                    )
                else:
                    vs.append(f"{value:.4f}")

                    print(f"{measure}: {value:.4f}")
                values['measure']=vs
        # 当前波动率：0.0151
        # 风险价值：-0.0268
        # 预期亏损：-0.0369
        # 贝塔系数：1.0000
        # 夏普比率：-1.1810
        # 排序比率：-1.7234
        # 最大回撤：-0.4101
        # 长期波动率预测：[显示前 5 个值] [0.015056188218295574, 0.03184530884027481, 0.023553188890218735, 0.008299920707941055]
        # 'Current_Volatility': [],
        # 'Value_at_Risk': [],
        # 'Expected_Shortfall': [],
        # 'Beta': [],
        # 'Sharpe_Ratio': [],
        # 'Sortino_Ratio': [],
        # 'Max_Drawdown': [],
        # 'Long_Term_Volatility_Forecast': []
        data = {'股票、证券代码': stocknames, '当前波动率': values['Current_Volatility']
                , '风险价值': values['Value_at_Risk'], '预期亏损': values['Expected_Shortfall']
                , '贝塔系数': values['Beta'], '夏普比率': values['Sharpe_Ratio']
                , '排序比率': values['Sortino_Ratio'], '最大回撤': values['Max_Drawdown']
                , '长期波动率预测': values['Long_Term_Volatility_Forecast']}

        df = pd.DataFrame(data)

        # print(df)
    finally:
        # Ensure we stop the continuous training when done
        risk_assessor.stop_continuous_training()
    return df

if st.button("分析风险"):
    # Run CrewAI analysis
    with st.spinner("风险分析进行中（大约需要1分钟）..."):
        result = run_analysis(stock_symbol)

    st.header("风险分析报告")
    st.markdown(result.to_markdown())
