import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from code_fin.Financial.crew1 import run_analysis
import json

st.set_page_config(layout="wide")
st.title("高级股票分析Agent")
st.markdown("""
一款由 AI Agent提供支持的高级股票分析工具，使用开源语言模型提供全面的财务分析。该应用程序结合了技术分析、基本面分析和情绪分析，为股票市场投资提供详细见解。

## 特征
- 实时股票数据分析
- 通过图表模式识别进行技术分析
- 公司财务的基本面分析
- 市场情绪分析
- 风险评估
- 竞争对手分析
- 投资策略建议
- 交互式图表和可视化
""")


openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))

# User input
stock_symbol = st.text_input("输入股票代码 (e.g., AAPL):", "AAPL")

if st.button("分析股票"):
    # Run CrewAI analysis
    with st.spinner("全面的股票分析进行中（大约需要5分钟）..."):
        result = run_analysis(stock_symbol,openai_api_base_url,openai_api_model_type,openai_api_key)

    # Parse the result
    # print(result)
    try:
        analysis = json.loads(result)
    except Exception as e:
        analysis = {}
        print(result.json_dict)
        print(result.tasks_output)
        # print(result.)
        print(result)

    # Display analysis result
    st.header("AI分析报告")

    # st.subheader("Analysis")
    st.write(result.raw)

    # col1, col2 = st.columns(2)
    #
    # with col1:
    #     st.subheader("Technical Analysis")
    #     st.write(analysis.get('technical_analysis', 'No technical analysis available'))
    #
    #     st.subheader("Chart Patterns")
    #     st.write(analysis.get('chart_patterns', 'No chart patterns identified'))
    #
    # with col2:
    #     st.subheader("Fundamental Analysis")
    #     st.write(analysis.get('fundamental_analysis', 'No fundamental analysis available'))
    #
    #     st.subheader("Sentiment Analysis")
    #     st.write(analysis.get('sentiment_analysis', 'No sentiment analysis available'))
    #
    # st.subheader("Risk Assessment")
    # st.write(analysis.get('risk_assessment', 'No risk assessment available'))
    #
    # st.subheader("Competitor Analysis")
    # st.write(analysis.get('competitor_analysis', 'No competitor analysis available'))
    #
    # st.subheader("Investment Strategy")
    # st.write(analysis.get('investment_strategy', 'No investment strategy available'))

    # Fetch stock data for chart
    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period="1y")

    # Create interactive chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=hist.index,
                                 open=hist['Open'],
                                 high=hist['High'],
                                 low=hist['Low'],
                                 close=hist['Close'],
                                 name='Price'))

    # Add volume bars
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', yaxis='y2'))

    # Add moving averages
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=50).mean(), name='50-day MA'))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=200).mean(), name='200-day MA'))

    fig.update_layout(
        title=f"{stock_symbol} 股票分析",
        yaxis_title='Price',
        yaxis2=dict(title='Volume', overlaying='y', side='right'),
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display key statistics
    st.subheader("关键统计数据")
    info = stock.info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
        st.metric("P/E Ratio", round(info.get('trailingPE', 0), 2))
    with col2:
        st.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 0):,.2f}")
        st.metric("52 Week Low", f"${info.get('fiftyTwoWeekLow', 0):,.2f}")
    with col3:
        st.metric("Dividend Yield", f"{info.get('dividendYield', 0):.2%}")
        st.metric("Beta", round(info.get('beta', 0), 2))