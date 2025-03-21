# Import the required libraries
import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.tools.serpapi import SerpApiTools
# from agno.models.anthropic import Claude
from textwrap import dedent

# Set up the Streamlit app
st.title("🎬 AI 电影制作代理")
# st.caption("Bring your movie ideas to life with the teams of script writing and casting AI agents")
st.markdown("""
这款 Streamlit 应用是一款人工智能电影制作助手，它使用LLM帮助您将电影创意变为现实。它可自动执行剧本编写和选角流程，让您轻松创作引人入胜的电影概念。
### 特征
- 根据您的电影创意、类型和目标观众生成剧本大纲
- 根据演员过往表现和当前空闲时间，推荐适合主要角色的演员
- 提供简明的电影概念概述
### 它是如何工作的？
AI电影制作代理利用三个主要组件：
- **编剧**：根据给定的电影构思和类型，制定包含人物描述和关键情节点的引人入胜的剧本大纲。
- **选角导演**：根据演员过往的表现和目前的时间安排，为主角推荐合适的演员。
- **电影制片人**：监督整个过程，协调编剧和选角导演之间的关系，并提供简明的电影概念概述。
""")
with st.sidebar:
    st.title("API Keys Configuration")
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password",value=st.session_state.get('openai_api_key'))
    openai_api_model_type = st.sidebar.text_input("OpenAI API Model Type", value=st.session_state.get('openai_api_model_type'))
    openai_api_base_url= st.sidebar.text_input("OpenAI API Base URL", value=st.session_state.get('openai_api_base_url'))
    serpapi_api_key = st.text_input("Enter your SerpAPI Key", type="password",value=st.session_state.get('serpapi_api_key'))

if openai_api_key and serpapi_api_key:
    script_writer = Agent(
        name="ScriptWriter",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url),
        description=dedent(
            """\
        You are an expert screenplay writer. Given a movie idea and genre, 
        develop a compelling script outline with character descriptions and key plot points.
        """
        ),
        instructions=[
            "Write a script outline with 3-5 main characters and key plot points.",
            "Outline the three-act structure and suggest 2-3 twists.",
            "Ensure the script aligns with the specified genre and target audience.",
        ],
    )

    casting_director = Agent(
        name="CastingDirector",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url),
        description=dedent(
            """\
        You are a talented casting director. Given a script outline and character descriptions,
        suggest suitable actors for the main roles, considering their past performances and current availability.
        """
        ),
        instructions=[
            "Suggest 2-3 actors for each main role.",
            "Check actors' current status using `search_google`.",
            "Provide a brief explanation for each casting suggestion.",
            "Consider diversity and representation in your casting choices.",
        ],
        tools=[SerpApiTools(api_key=serpapi_api_key)],
    )

    movie_producer = Agent(
        name="MovieProducer",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url),
        team=[script_writer, casting_director],
        description="Experienced movie producer overseeing script and casting.",
        instructions=[
            "Ask ScriptWriter for a script outline based on the movie idea.",
            "Pass the outline to CastingDirector for casting suggestions.",
            "Summarize the script outline and casting suggestions.",
            "Provide a concise movie concept overview.",
        ],
        markdown=True,
    )

    # Input field for the report query
    movie_idea = st.text_area("Describe your movie idea in a few sentences:")
    genre = st.selectbox("Select the movie genre:", 
                         ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance", "Thriller"])
    target_audience = st.selectbox("Select the target audience:", 
                                   ["General", "Children", "Teenagers", "Adults", "Mature"])
    estimated_runtime = st.slider("Estimated runtime (in minutes):", 60, 180, 120)

    # Process the movie concept
    if st.button("Develop Movie Concept"):
        with st.spinner("Developing movie concept..."):
            input_text = (
                f"Movie idea: {movie_idea}, Genre: {genre}, "
                f"Target audience: {target_audience}, Estimated runtime: {estimated_runtime} minutes"
            )
            # Get the response from the assistant
            response = movie_producer.run(input_text, stream=False)
            st.write(response)