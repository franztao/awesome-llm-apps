import streamlit as st

import os
import autogen
from textwrap import dedent
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "code_fin", "FinRobot"))
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
财经年度分析报告Agent是一款基于Streamlit的交互式应用，帮助用户快速生成专业财经年度分析报告。它提供数据可视化、关键指标分析和自动化报告生成功能，支持多种财经数据类型，适用于投资者、分析师和企业决策者，简化财经数据分析流程，提升报告效率。
  """)

openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                              value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))


def get_report(company, fyear, openai_api_key, openai_api_model_type, openai_api_base_url):
    llm_config = {
        "config_list": [

            {
                "model": openai_api_model_type,
                "api_key": openai_api_key,
                "base_url": openai_api_base_url
            }
        ],
        "timeout": 120,
        "temperature": 0.5,
        # "max_tokens": 8192
    }
    print(llm_config)

    register_keys_from_json(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "code_fin", "FinRobot", "config_api_keys"))
    # register_keys_from_json(
    #     r"C:\Users\m01216.METAX-TECH\Desktop\code\awesome-llm-apps\code_fin\FinRobot\config_api_keys")

    # Intermediate results will be saved in this directory

    work_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "_".join([company, fyear]))
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


if openai_api_key:

    # company = "Microsoft"
    # fyear = "2023"
    col1, col2 = st.columns(2)
    with col1:
        # stock1 = st.text_input("Enter first stock symbol (e.g. AAPL)")
        stock1 = st.text_input("公司 (e.g. Microsoft)", "Microsoft")
    with col2:
        # stock2 = st.text_input("Enter second stock symbol (e.g. MSFT)")
        stock2 = st.text_input("年份 (e.g. 2023)", "2023")

    if stock1 and stock2:
        if st.button("生成报告"):
            with st.spinner(f"分析公司{stock1}和年份{stock2}（大约需要5分钟，请耐心等候）..."):
                paths = get_report(stock1, stock2, openai_api_key, openai_api_model_type, openai_api_base_url)
            # paths = r'C:\Users\m01216.METAX-TECH\Downloads\FinRobot-master\FinRobot-master\report'
            fs = os.listdir(paths)
            for f in fs:
                if f.endswith(".pdf"):
                    print(f)
                    print("生成的分析报告")
                    st.subheader("生成的分析报告")
                    st_display_pdf(os.path.join(paths, f))
