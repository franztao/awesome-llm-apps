import streamlit as st
# from pages import ai_investment_agent
st.set_page_config(
    page_title="沐曦Agent智能体",
    page_icon="👋",
)

# page1 = st.Page("pages/1_📈AI智能投资Agent.py", title="页面1")
# page2 = st.Page("pages/2_‍⚖️AI法律agent团队.py", title="页面2")
#
# pg = st.navigation([page1, page2])
# pg.run()

# st.sidebar.page_link(r"pages/1_📈AI智能投资Agent.py", label="📈AI智能投资Agent")
# st.sidebar.page_link(r"pages/2_‍⚖️AI法律agent团队.py", label="👨‍⚖️AI法律agent团队")
# st.sidebar.page_link(r"pages/3_💼AI招聘Agent团队.py", label="💼AI招聘Agent团队")
# st.sidebar.page_link(r"pages/4_🧲AI竞争对手情报Agent团队.py", label="🧲AI竞争对手情报Agent团队")
# st.sidebar.page_link(r"pages/5_♂️AI健康与健身规划Agent.py", label="️‍♂️AI健康与健身规划Agent")
# st.sidebar.page_link(r"pages/6_📈AI初创企业趋势分析Agent.py", label="️📈AI初创企业趋势分析Agent")
# st.sidebar.page_link(r"pages/7_🗞️AI记者Agent.py", label="️🗞️AI记者Agent")
# st.sidebar.page_link(r"pages/8_🎯AI潜在客户生成Agent.py", label="🎯AI潜在客户生成Agent")
# st.sidebar.page_link(r"pages/9_💰AI个人财务Agent.py", label="💰AI个人财务Agent")
# st.sidebar.page_link(r"pages/10_🩻AI医学影像诊断Agent.py", label="🩻AI医学影像诊断Agent")
# st.sidebar.page_link(r"pages/11_👨‍🏫AI教学Agent团队.py", label="👨‍🏫AI教学Agent团队")
# st.sidebar.page_link(r"pages/12_🛫AI智能旅行社.py", label="🛫AI智能旅行社")
# st.sidebar.page_link(r"pages/13_🎬AI电影制作Agent.py", label="🎬AI电影制作Agent")
# st.sidebar.page_link(r"pages/14_💻多模态AI编码Agent团队.py", label="💻多模态AI编码Agent团队")
# # st.sidebar.page_link(r"pages/ai_meeting_agent.py", label="📝 AI 会议准备Agent")
# st.sidebar.page_link(r"pages/15_♜白Agentvs黑Agent棋局对决.py", label="♜白Agentvs黑Agent:棋局对决")
# st.sidebar.page_link(r"pages/16_🏠AI智能房地产经纪人.py", label="🏠AI智能房地产经纪人")
# # st.sidebar.page_link(r"pages/ai_mutimodal_agent.py", label="🧬 多模态 AI Agent")
# st.sidebar.page_link(r"pages/17_🌍AQI分析Agent.py", label="🌍AQI分析Agent")
# # st.sidebar.page_link(r"pages/ai_customer_support_agent.py", label="🛒 AI 客户支持Agent")
# st.sidebar.page_link(r"pages/18_🤖AI系统架构师顾问.py", label="🤖AI系统架构师顾问")



st.write("# 欢迎使用 沐曦Agent智能体! 👋")
# st.write(
#     "A curated collection of awesome LLM apps built with RAG and AI agents. This repository features LLM apps that use models from OpenAI, Anthropic, Google, and open-source models like DeepSeek, Qwen or Llama that you can run locally on your computer.")
st.write(
    "精选的 LLM 应用集合，使用 RAG 和 AI Agent构建。此存储库包含使用 OpenAI、Anthropic、Google 的模型以及 DeepSeek、Qwen 或 Llama 等开源模型的 LLM 应用，您可以在计算机上本地运行这些应用。")

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

# OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url)
openai_api_key = st.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
st.session_state['openai_api_key'] = openai_api_key
openai_api_model_type = st.text_input("LLM API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
st.session_state['openai_api_model_type'] = openai_api_model_type
openai_api_vlm_model_type = st.text_input("VLM API Model Type",
                                          value=st.session_state.get('openai_api_vlm_model_type'))
st.session_state['openai_api_vlm_model_type'] = openai_api_vlm_model_type
openai_api_embedding_model_type = st.text_input("Embedding API  Model Type",
                                                value=st.session_state.get('openai_api_embedding_model_type'))
st.session_state['openai_api_embedding_model_type'] = openai_api_embedding_model_type
openai_api_base_url = st.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
st.session_state['openai_api_key'] = openai_api_key
# st.caption(" Get your LLM API Key from [OpenAI's website](https://platform.openai.com/api-keys)")

firecrawl_api_key = st.text_input("Firecrawl API Key", type="password", value=st.session_state.get('firecrawl_api_key'))
st.session_state['firecrawl_api_key'] = firecrawl_api_key
st.caption(" Get your Firecrawl API key from [Firecrawl's website](https://www.firecrawl.dev/app/api-keys)")

composio_api_key = st.text_input("Composio API Key", type="password", value=st.session_state.get('composio_api_key'))
st.session_state['composio_api_key'] = composio_api_key
st.caption(" Get your Composio API key from [Composio's website](https://composio.ai)")

perplexity_api_key = st.text_input("Perplexity API Key", type="password", value=st.session_state.get('perplexity_api_key'))
st.session_state['perplexity_api_key'] = perplexity_api_key
exa_api_key = st.text_input("Exa API Key", type="password", value=st.session_state.get('exa_api_key'))
st.session_state['exa_api_key'] = exa_api_key

serpapi_api_key = st.text_input("Enter your SerpAPI Key", type="password", value=st.session_state.get('serpapi_api_key'))
st.session_state['serpapi_api_key'] = serpapi_api_key

e2b_key = st.text_input("E2B API Key", value=st.session_state.get('e2b_key'),
                                         type="password")
st.session_state['e2b_key'] = e2b_key
#

st.subheader("Zoom Settings")
zoom_account_id = st.text_input("Zoom Account ID", type="password", value=st.session_state.get('zoom_account_id'))
st.session_state['zoom_account_id'] = zoom_account_id
zoom_client_id = st.text_input("Zoom Client ID", type="password", value=st.session_state.get('zoom_client_id'))
st.session_state['zoom_client_id'] = zoom_client_id
zoom_client_secret = st.text_input("Zoom Client Secret", type="password",
                                   value=st.session_state.get('zoom_client_secret'))
st.session_state['zoom_client_secret'] = zoom_client_secret

st.subheader("Email Settings")
email_sender = st.text_input("Sender Email", value=st.session_state.get('email_sender'),
                             help="Email address to send from")
st.session_state['email_sender'] = email_sender
email_passkey = st.text_input("Email App Password", type="password", value=st.session_state.get('email_passkey'),
                              help="App-specific password for email")
st.session_state['email_passkey'] = email_passkey
company_name = st.text_input("Company Name", value=st.session_state.get('company_name'),
                             help="Name to use in email communications")
st.session_state['company_name'] = company_name

st.subheader("Qdrant Settings")
qdrant_url = st.text_input("qdrant_url", value=st.session_state.get('qdrant_url'))
st.session_state['qdrant_url'] = qdrant_url
qdrant_api_key = st.text_input("qdrant_api_key", value=st.session_state.get('qdrant_api_key'))
st.session_state['qdrant_api_key'] = qdrant_api_key


st.session_state['openai_api_model_type'] = "Qwen2.5-Coder-32B-Instruct"
st.session_state['openai_api_key'] = 'VAIKKIMZVDLDET6H8NJGJCW9OE4T6P5VODKKNMW6'
st.session_state['openai_api_base_url'] = 'https://ai.gitee.com/v1'


# st.session_state['openai_api_model_type'] = "qwen-plus"
# st.session_state['openai_api_key'] = 'sk-f7f3039f52e3402bbafda926f4da7cb3'
# st.session_state['openai_api_base_url'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
st.session_state['firecrawl_api_key'] = 'fc-bd7f59397c2544e79a7236038b0ba662'
st.session_state['composio_api_key'] = '8fsy14yf2vd3nuekyc03g5'

st.session_state['e2b_key'] = 'sk_e2b_cd993c89f425970130e118828cfd78dbbad08394'
# zoom_tools = CustomZoomTool(
#     account_id='CRGZvs0ARnaGntbxJuFjbw',
#     client_id='dmp7GbYhSICJERYeIF5M6w',
#     client_secret='6zKv8ANAycFZTUQ8SfGicAsMGrrq6MOg'
# )
st.session_state['zoom_account_id'] = 'CRGZvs0ARnaGntbxJuFjbw'
st.session_state['zoom_client_id'] = 'dmp7GbYhSICJERYeIF5M6w'
st.session_state['zoom_client_secret'] = '6zKv8ANAycFZTUQ8SfGicAsMGrrq6MOg'

# tools=[EmailTools(
#             receiver_email=st.session_state.candidate_email,
#             sender_email='franztaoheng@gmail.com',
#             sender_name='muxi tao',
#             sender_passkey='ynzr izpr amec imlz'
#         )],
st.session_state['email_sender'] = 'franztaoheng@gmail.com'
st.session_state['email_passkey'] = 'ynzr izpr amec imlz'
st.session_state['company_name'] = 'muxi tao'

st.session_state['exa_api_key'] = '94692c17-1768-426e-8828-b41b4dab63b1'

st.session_state['serpapi_api_key'] = '4daaca7da2c5287775d7783777c9b416cd91ac961ff24cb41ddb45f7c7176a19'

st.session_state['qdrant_url'] = "http://localhost:6333/"
st.session_state['qdrant_api_key'] = "123"


# st.session_state['openai_api_embedding_model_type'] = "text-embedding-v3"
# st.session_state['openai_api_vlm_model_type'] = "qwen_vl_plus"

st.session_state['openai_api_embedding_model_type'] = "bge-large-zh-v1.5"
st.session_state['openai_api_vlm_model_type'] = "Qwen2-VL-72B"

