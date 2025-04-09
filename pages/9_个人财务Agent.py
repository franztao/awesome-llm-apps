from textwrap import dedent
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
import streamlit as st
from agno.models.openai import OpenAIChat, OpenAILike

# Set up the Streamlit app
st.title("💰 AI个人财务Agent")
# st.caption("Manage your finances with AI Personal Finance Manager by creating personalized budgets, investment plans, and savings strategies using GPT-4o")
st.markdown("""这款 Agent  应用是一款人工智能个人理财规划器，可使用LLM生成个性化财务计划。它可以自动完成研究、规划和创建量身定制的预算、投资策略和储蓄目标的过程，让您轻松掌控自己的财务未来。
### 特征
- 设定您的财务目标并提供有关您当前财务状况的详细信息
- 使用LLM生成智能个性化的财务建议
- 获得定制的预算、投资计划和储蓄策略
""")
# Get LLM API Key from user
openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
# OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url)
# Get SerpAPI key from the user
serp_api_key = st.sidebar.text_input("Enter Serp API Key for Search functionality", type="password", value=st.session_state.get('serpapi_api_key'))

if openai_api_key and serp_api_key:
    researcher = Agent(
        name="Researcher",
        role="Searches for financial advice, investment opportunities, and savings strategies based on user preferences",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        description=dedent(
            """\
        You are a world-class financial researcher. Given a user's financial goals and current financial situation,
        generate a list of search terms for finding relevant financial advice, investment opportunities, and savings strategies.
        Then search the web for each term, analyze the results, and return the 10 most relevant results.
        """
        ),
        instructions=[
            "Given a user's financial goals and current financial situation, first generate a list of 3 search terms related to those goals.",
            "For each search term, `search_google` and analyze the results.",
            "From the results of all searches, return the 10 most relevant results to the user's preferences.",
            "Remember: the quality of the results is important.",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],
        add_datetime_to_instructions=True,
    )
    planner = Agent(
        name="Planner",
        role="Generates a personalized financial plan based on user preferences and research results",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        description=dedent(
            """\
        You are a senior financial planner. Given a user's financial goals, current financial situation, and a list of research results,
        your goal is to generate a personalized financial plan that meets the user's needs and preferences.
        """
        ),
        instructions=[
            "Given a user's financial goals, current financial situation, and a list of research results, generate a personalized financial plan that includes suggested budgets, investment plans, and savings strategies.",
            "Ensure the plan is well-structured, informative, and engaging.",
            "Ensure you provide a nuanced and balanced plan, quoting facts where possible.",
            "Remember: the quality of the plan is important.",
            "Focus on clarity, coherence, and overall quality.",
            "Never make up facts or plagiarize. Always provide proper attribution.",
        ],
        add_datetime_to_instructions=True,
    )

    # Input fields for the user's financial goals and current financial situation
    financial_goals = st.text_input("您的财务目标是什么？")
    current_situation = st.text_area("描述您目前的财务状况")

    if st.button("制定财务计划"):
        with st.spinner("Processing..."):
            # Get the response from the assistant
            response = planner.run(f"Financial goals: {financial_goals}, Current situation: {current_situation}", stream=False)
            st.write(response.content)
