import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.tools.yfinance import YFinanceTools

st.set_page_config(page_title="智能选股投资Agent", page_icon="👨📈")

st.title("📈 智能选股投资Agent")
# st.caption("This app allows you to compare the performance of two stocks and generate detailed reports.")
st.markdown("""
    这款 Agent  应用是一款基于 AI 的投资Agent，采用 Agno 的 AI Agent 框架构建，可比较两只股票的表现并生成详细报告。通过将 LLM 与 Yahoo Finance 数据结合使用，这款应用可提供有价值的见解，帮助您做出明智的投资决策。
    ### 特征
    - 比较两只股票的表现
    - 检索全面的公司信息
    - 获取最新的公司新闻和分析师建议
""")

openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
if openai_api_key:
    assistant = Agent(
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        tools=[
            YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True)
        ],
        show_tool_calls=True,
        description="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals.",
        instructions=[
            "Format your response using markdown and use tables to display data where possible."
        ],
        debug_mode=True
    )

    col1, col2 = st.columns(2)
    with col1:
        # stock1 = st.text_input("Enter first stock symbol (e.g. AAPL)")
        stock1 = st.text_input("输入第一个股票代码 (e.g. AAPL)","AAPL")
    with col2:
        # stock2 = st.text_input("Enter second stock symbol (e.g. MSFT)")
        stock2 = st.text_input("输入第二个股票代码 (e.g. MSFT)","MSFT")

    if stock1 and stock2:
        if st.button("进行分析"):
            with st.spinner(f"对比 {stock1} 和 {stock2}（大约需要5分钟，请耐心等候）......"):
                query = f"Compare both the stocks - {stock1} and {stock2} and make a detailed report for an investment trying to invest and compare these stocks"
                response = assistant.run(query, stream=False)
                st.markdown(response.content)
