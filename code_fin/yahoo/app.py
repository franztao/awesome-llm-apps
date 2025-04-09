import os
import openai
import streamlit as st

from dotenv import load_dotenv, find_dotenv
from code_fin.yahoo.tools import get_historical_data, get_stock_info, get_stock_actions, get_shares_count, get_financials, \
    get_holders_info, get_recommendations, get_options_expiration_dates, get_option_chain, get_stock_news
from code_fin.yahoo.utils import run_agent, create_chain, tool_registry
from langchain.agents import AgentExecutor
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
from langchain.schema import ChatMessage
from langchain.memory import ConversationBufferMemory

def load_app():
    _ = load_dotenv(find_dotenv())  # read local .env file
    # openai.api_key = os.environ['OPENAI_API_KEY']

    st.set_page_config(layout="wide")


    openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
    openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                                  value=st.session_state.get('openai_api_model_type'))
    openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))

    def register_tools():
        if not hasattr(tool_registry, "_is_registered"):
            tool_registry.register_tool("get_stock_info", get_stock_info)
            tool_registry.register_tool("get_historical_data", get_historical_data)
            tool_registry.register_tool("get_stock_actions", get_stock_actions)
            tool_registry.register_tool("get_shares_count", get_shares_count)
            tool_registry.register_tool("get_financials", get_financials)
            tool_registry.register_tool("get_holders_info", get_holders_info)
            tool_registry.register_tool("get_recommendations", get_recommendations)
            tool_registry.register_tool("get_options_expiration_dates", get_options_expiration_dates)
            tool_registry.register_tool("get_option_chain", get_option_chain)
            tool_registry.register_tool("get_stock_news", get_stock_news)

            # Mark as registered
            tool_registry._is_registered = True


    # Register the tools if not already registered
    register_tools()

    # Load the tools from the registry
    tools = tool_registry.get_tools()

    # Sidebar for selecting the OpenAI model
    # st.sidebar.markdown("### Select OpenAI Model")
    # model_options = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo-0125"]
    # selected_model = st.sidebar.selectbox("Choose a model:", model_options, index=model_options.index("gpt-3.5-turbo-0125"))

    # Create the agent chain
    agent_chain = create_chain(tools,openai_api_base_url,openai_api_model_type,openai_api_key)

    # Create the memory for storing conversation history
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True, memory=memory)

    st.title("实时财经洞察Agent")

    st.markdown("""
    欢迎使用实时财经洞察助手！此应用程序利用 LLM、Langchain Agents 和 Yahoo Finance Python 库为您提供最新的财务数据和洞察。无论您对股票价格、公司财务状况还是最新消息感兴趣，此助手都可以为您提供帮助。
    
    ##### 功能：
    - **股票信息**：获取有关任何股票的详细信息，包括历史数据和最新消息。
    - **财务报表**：访问年度和季度损益表、资产负债表和现金流量表。
    - **期权数据**：探索可用的期权到期日和详细的期权链。
    - **持有人和建议**：查看有关主要持有人、内幕交易和分析师建议的信息。
    """)

    # Sidebar for Sample Questions
    st.sidebar.markdown("### 示例问题")
    sample_questions = {
        "股票信息": [
            "给我关于微软的信息"
            "苹果现在的价格是多少？",
            "给我特斯拉过去一个月的历史数据",
            "微软的最新新闻文章是什么？"
        ],
        "财务报表": [
            "给我看看谷歌的最新损益表",
            "亚马逊的季度现金流是多少？",
            "你能提供 Facebook 的年度资产负债表吗？",
            "请提供亚马逊的季度资产负债表"
        ],
        "拆分和股息": [
            "给我高盛的股息和拆分",
            "给我苹果的拆分",
            "给我可口可乐的股息"
        ],
        "股票数量": [
            "告诉我自 2022 年 1 月 1 日以来微软的流通股数量",
            "微软有多少股微软在 2022 年 1 月 1 日至 2022 年 12 月 31 日期间有多少未偿还的股票？",
            "微软最近未偿还的股票数量是多少？",
        ],
        "期权数据": [
            "苹果有哪些期权到期日？",
            "请向我展示 2024-01-19 到期的特斯拉期权链"
        ],
        "持有人和推荐": [
            "Netflix 的主要持有者是谁？",
            "哪些共同基金持有亚马逊的股份最多？",
            "分析师最近对特斯拉有什么建议？",
            "请向我展示微软最近的内幕交易",
            "谷歌的可持续性得分是多少？",
            "您能提供特斯拉最新建议的摘要吗？"
        ]
    }

    # Display Sample Questions in the Sidebar with Expanders
    for category, questions in sample_questions.items():
        with st.sidebar:
            with st.expander(f"{category}"):
                for question in questions:
                    st.markdown(f"- {question}")

    # TODO: Accept OpenAI API key as input in sidebar

    if "messages" not in st.session_state:
        st.session_state["messages"] = [ChatMessage(role="assistant", content="我能帮你什么？")]

    # Display the chat messages already in the session state
    for msg in st.session_state.messages:
        st.chat_message(msg.role).write(msg.content)

    if prompt := st.chat_input():
        # add the user message to the session state
        st.session_state.messages.append(ChatMessage(role="user", content=prompt))

        # display the user message in the chat
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            # Uncomment the following lines to enable Streamlit callbacks and display agent execution

            # st_callback = StreamlitCallbackHandler(st.container())
            # response = agent_executor.invoke(
            #     {"input": prompt}, {"callbacks": [st_callback]}
            # )
            try:
                response = agent_executor.invoke(
                    {"input": prompt}
                )
                st.write(response["output"])
                st.session_state.messages.append(ChatMessage(role="assistant", content=response["output"]))
            except Exception as e:
                st.write(f"An error occurred: {e}")
                st.session_state.messages.append(
                    ChatMessage(role="assistant", content="An error occurred. Please try again."))