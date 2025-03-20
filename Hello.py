import streamlit as st

st.set_page_config(
    page_title="你好",
    page_icon="👋",
)

st.sidebar.page_link(r"pages/ai_lead_generation_agent.py", label="👨‍⚖️ AI 法律agent团队")
# st.sidebar.page_link("pages/weather_country.py", label="天气")

st.write("# 欢迎使用 沐曦Agent智能体! 👋")
st.write(
    "A curated collection of awesome LLM apps built with RAG and AI agents. This repository features LLM apps that use models from OpenAI, Anthropic, Google, and open-source models like DeepSeek, Qwen or Llama that you can run locally on your computer.")

st.sidebar.success("在上方选择一个演示。")
# st.markdown(
#     """
#     Streamlit 是一个专为机器学习和数据科学项目而构建的开源应用框架。
#     **👈 从侧边栏选择一个演示**，看看 Streamlit 能做什么吧！
#     ### 想了解更多吗？
#     - 查看 [streamlit.io](https://streamlit.io)
#     - 阅读我们的 [文档](https://docs.streamlit.io)
#     - 在我们的 [社区论坛](https://discuss.streamlit.io) 提问
#     ### 查看更复杂的示例
#     - 使用神经网络来 [分析 Udacity 自动驾驶汽车图像数据集](https://github.com/streamlit/demo-self-driving)
#     - 探索一个 [纽约市乘车数据集](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )
st.header("API Keys")
# OpenAILike(id="qwen-max", api_key='sk-f7f3039f52e3402bbafda926f4da7cb3',
#                          base_url='https://dashscope.aliyuncs.com/compatible-mode/v1')


openai_api_key = st.text_input("Similar OpenAI API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.text_input("OpenAI API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.text_input("OpenAI API Base URL", value=st.session_state.get('openai_api_base_url'))
st.session_state['openai_api_key'] = openai_api_key

st.caption(" Get your OpenAI API key from [OpenAI's website](https://platform.openai.com/api-keys)")

firecrawl_api_key = st.text_input("Firecrawl API Key", type="password", value=st.session_state.get('firecrawl_api_key'))
st.session_state['firecrawl_api_key'] = firecrawl_api_key
st.caption(" Get your Firecrawl API key from [Firecrawl's website](https://www.firecrawl.dev/app/api-keys)")

composio_api_key = st.text_input("Composio API Key", type="password", value=st.session_state.get('composio_api_key'))
st.session_state['composio_api_key'] = composio_api_key
st.caption(" Get your Composio API key from [Composio's website](https://composio.ai)")

st.session_state['openai_api_model_type'] = "qwen-max"
st.session_state['openai_api_key'] = 'sk-f7f3039f52e3402bbafda926f4da7cb3'
st.session_state['openai_api_base_url'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
st.session_state['firecrawl_api_key'] = 'fc-bd7f59397c2544e79a7236038b0ba662'
st.session_state['composio_api_key'] ='8fsy14yf2vd3nuekyc03g5'