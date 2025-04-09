import streamlit as st

import os
import autogen
from textwrap import dedent
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "code_fin","FinRobot"))
print(sys.path)
from code_fin.FinRobot.finrobot.utils import register_keys_from_json
from code_fin.FinRobot.finrobot.agents.workflow import SingleAssistantShadow

import streamlit as st
import base64


# 显示PDF文件的函数
def st_display_pdf(pdf_file):
    with open(pdf_file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)


# Setting up Streamlit app
st.title("财经年度分析报告Agent")
# st.caption("Get the latest trend analysis and startup opportunities based on your topic of interest in a click!.")
st.markdown("""
AI 创业趋势分析Agent是一款面向新兴企业家的工具，可通过识别新兴趋势、潜在市场空白和特定行业的增长机会来生成可操作的见解。企业家可以利用这些数据驱动的见解来验证想法、发现市场机会并对其创业项目做出明智的决策。它结合 Newspaper4k 和 DuckDuckGo 来扫描和分析以创业公司为重点的文章和市场数据。它使用LLM 来处理这些信息以提取新兴模式并使企业家能够识别有前途的创业机会。
  ### 特征
  - **用户提示**：创业者可以输入自己感兴趣的具体创业领域或者技术进行研究。
  - **新闻收集**：该Agent使用 DuckDuckGo 收集最近的创业新闻、融资轮次和市场分析。
  - **摘要生成**：使用 Newspaper4k 生成已验证信息的简明摘要。
  - **趋势分析**：系统通过分析的故事识别初创企业资金、技术采用和市场机会方面的新兴模式。
  - **Streamlit UI**：该应用程序具有使用 Streamlit 构建的用户友好界面，可轻松进行交互。
  """)


def get_report(company, fyear):
    llm_config = {
        "config_list": autogen.config_list_from_json(
            r"C:\Users\m01216.METAX-TECH\Desktop\code\awesome-llm-apps\code_fin\FinRobot\OAI_CONFIG_LIST",
            filter_dict={
                "model": ["deepseek/deepseek-chat"],
            },
        ),
        "timeout": 120,
        "temperature": 0.5,
        # "max_tokens": 8192
    }
    register_keys_from_json(
        r"C:\Users\m01216.METAX-TECH\Desktop\code\awesome-llm-apps\code_fin\FinRobot\config_api_keys")

    # Intermediate results will be saved in this directory

    work_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "report0408")
    os.makedirs(work_dir, exist_ok=True)

    assistant = SingleAssistantShadow(
        "Expert_Investor",
        llm_config,
        max_consecutive_auto_reply=None,
        human_input_mode="TERMINATE",
    )

    message = dedent(
        f"""
        With the tools you've been provided, write an annual report based on {company}'s {fyear} 10-k report, format it into a pdf.
        Pay attention to the followings:
        - Explicitly explain your working plan before you kick off.
        - Use tools one by one for clarity, especially when asking for instructions. 
        - All your file operations should be done in "{work_dir}". 
        - Display any image in the chat once generated.
        - All the paragraphs should combine between 400 and 450 words, don't generate the pdf until this is explicitly fulfilled.
    """
    )

    assistant.chat(message, use_cache=True, max_turns=50,
                   summary_method="last_msg")
    return work_dir


openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                              value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
if openai_api_key:

    # company = "Microsoft"
    # fyear = "2023"
    col1, col2 = st.columns(2)
    with col1:
        # stock1 = st.text_input("Enter first stock symbol (e.g. AAPL)")
        stock1 = st.text_input("company (e.g. Microsoft)")
    with col2:
        # stock2 = st.text_input("Enter second stock symbol (e.g. MSFT)")
        stock2 = st.text_input("fyear (e.g. 2023)")

    if stock1 and stock2:
        with st.spinner(f"Analyzing {stock1} and {stock2}..."):
            paths = get_report(stock1, stock2)

        fs = os.listdir(paths)
        for f in fs:
            if f.endswith(".pdf"):
                st.subheader("生成的分析报告")
                st_display_pdf(os.path.join(paths, f))
