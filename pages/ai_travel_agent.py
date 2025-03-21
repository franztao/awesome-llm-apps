from textwrap import dedent
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
import streamlit as st
from agno.models.openai import OpenAIChat, OpenAILike

# Set up the Streamlit app
st.title("AI智能旅行社 ✈️")
# st.caption("Plan your next adventure with AI Travel Planner by researching and planning a personalized itinerary on autopilot using GPT-4o")
st.markdown("""
这款 Streamlit 应用是一款人工智能旅行社，可使用LLM生成个性化旅行行程。它可自动完成您研究、规划和组织梦想假期的过程，让您轻松探索令人兴奋的目的地。
### 特征
- 研究并发现令人兴奋的旅游目的地、活动和住宿
- 根据你想要旅行的天数定制你的行程
- 利用LLM的力量生成智能个性化的旅行计划
### 它是如何工作的？
人工智能旅行社有两个主要组成部分：
- 研究员：负责根据用户的目的地和旅行时长生成搜索词，并使用 SerpAPI 在网络上搜索相关活动和住宿。
- 规划师：根据研究结果和用户偏好生成个性化的行程草案，其中包括建议的活动
""")
# Streamlit sidebar for API keys
with st.sidebar:
    st.title("API Keys Configuration")
    openai_api_key = st.text_input("Enter your LLM API Key", type="password",value=st.session_state.get('openai_api_key'))
    openai_api_model_type = st.sidebar.text_input("LLM API Model Type", value=st.session_state.get('openai_api_model_type'))
    openai_api_base_url= st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
    serpapi_api_key = st.text_input("Enter your SerpAPI Key", type="password",value=st.session_state.get('serpapi_api_key'))

if openai_api_key and serpapi_api_key:
    researcher = Agent(
        name="Researcher",
        role="Searches for travel destinations, activities, and accommodations based on user preferences",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url),
        description=dedent(
            """\
        You are a world-class travel researcher. Given a travel destination and the number of days the user wants to travel for,
        generate a list of search terms for finding relevant travel activities and accommodations.
        Then search the web for each term, analyze the results, and return the 10 most relevant results.
        """
        ),
        instructions=[
            "Given a travel destination and the number of days the user wants to travel for, first generate a list of 3 search terms related to that destination and the number of days.",
            "For each search term, `search_google` and analyze the results."
            "From the results of all searches, return the 10 most relevant results to the user's preferences.",
            "Remember: the quality of the results is important.",
        ],
        tools=[SerpApiTools(api_key=serpapi_api_key)],
        add_datetime_to_instructions=True,
    )
    planner = Agent(
        name="Planner",
        role="Generates a draft itinerary based on user preferences and research results",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url),
        description=dedent(
            """\
        You are a senior travel planner. Given a travel destination, the number of days the user wants to travel for, and a list of research results,
        your goal is to generate a draft itinerary that meets the user's needs and preferences.
        """
        ),
        instructions=[
            "Given a travel destination, the number of days the user wants to travel for, and a list of research results, generate a draft itinerary that includes suggested activities and accommodations.",
            "Ensure the itinerary is well-structured, informative, and engaging.",
            "Ensure you provide a nuanced and balanced itinerary, quoting facts where possible.",
            "Remember: the quality of the itinerary is important.",
            "Focus on clarity, coherence, and overall quality.",
            "Never make up facts or plagiarize. Always provide proper attribution.",
        ],
        add_datetime_to_instructions=True,
    )

    # Input fields for the user's destination and the number of days they want to travel for
    destination = st.text_input("Where do you want to go?")
    num_days = st.number_input("How many days do you want to travel for?", min_value=1, max_value=30, value=7)

    if st.button("Generate Itinerary"):
        with st.spinner("Researching your destination..."):
            # First get research results
            research_results = researcher.run(f"Research {destination} for a {num_days} day trip", stream=False)
            
            # Show research progress
            st.write("✓ Research completed")
            
        with st.spinner("Creating your personalized itinerary..."):
            # Pass research results to planner
            prompt = f"""
            Destination: {destination}
            Duration: {num_days} days
            Research Results: {research_results.content}
            
            Please create a detailed itinerary based on this research.
            """
            response = planner.run(prompt, stream=False)
            st.write(response.content)