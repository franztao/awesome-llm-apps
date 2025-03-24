# Import the required libraries
from textwrap import dedent

import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.serpapi import SerpApiTools

# Set up the Streamlit app
st.title("🗞️ AI记者Agent")
# st.caption("Generate High-quality articles with AI Journalist by researching, wriritng and editing quality articles on autopilot using GPT-4o")
st.markdown("""
这款 Agent  应用是一款由人工智能驱动的记者Agent，可使用LLM生成高质量文章。它可以自动执行研究、撰写和编辑文章的过程，让您轻松创建任何主题的引人入胜的内容。
### 特征
- 在网络上搜索关于特定主题的相关信息
- 撰写结构良好、内容丰富且引人入胜的文章
- 编辑和完善生成的内容以满足《纽约时报》的高标准
### 它是如何工作的？
人工智能记者Agent利用三个主要组件：
- 搜索器：负责根据给定的主题生成搜索词，并使用 SerpAPI 在网络上搜索相关的 URL。
- 作者：使用 NewspaperToolkit 从提供的 URL 中检索文本，并根据提取的信息撰写高质量的文章。
- 编辑：协调搜索者和作者之间的工作流程，并对生成的文章进行最终的编辑和完善。
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
    searcher = Agent(
        name="Searcher",
        role="Searches for top URLs based on a topic",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,
                           base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        description=dedent(
            """\
        You are a world-class journalist for the New York Times. Given a topic, generate a list of 3 search terms
        for writing an article on that topic. Then search the web for each term, analyse the results
        and return the 10 most relevant URLs.
        """
        ),
        instructions=[
            "Given a topic, first generate a list of 3 search terms related to that topic.",
            "For each search term, `search_google` and analyze the results."
            "From the results of all searcher, return the 10 most relevant URLs to the topic.",
            "Remember: you are writing for the New York Times, so the quality of the sources is important.",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],
        add_datetime_to_instructions=True,
    )
    writer = Agent(
        name="Writer",
        role="Retrieves text from URLs and writes a high-quality article",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        description=dedent(
            """\
        You are a senior writer for the New York Times. Given a topic and a list of URLs,
        your goal is to write a high-quality NYT-worthy article on the topic.
        """
        ),
        instructions=[
            "Given a topic and a list of URLs, first read the article using `get_article_text`."
            "Then write a high-quality NYT-worthy article on the topic."
            "The article should be well-structured, informative, and engaging",
            "Ensure the length is at least as long as a NYT cover story -- at a minimum, 15 paragraphs.",
            "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
            "Remember: you are writing for the New York Times, so the quality of the article is important.",
            "Focus on clarity, coherence, and overall quality.",
            "Never make up facts or plagiarize. Always provide proper attribution.",
        ],
        tools=[Newspaper4kTools()],
        add_datetime_to_instructions=True,
        markdown=True,
    )

    editor = Agent(
        name="Editor",
        model=OpenAILike(id=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        team=[searcher, writer],
        description="You are a senior NYT editor. Given a topic, your goal is to write a NYT worthy article.",
        instructions=[
            "Given a topic, ask the search journalist to search for the most relevant URLs for that topic.",
            "Then pass a description of the topic and URLs to the writer to get a draft of the article.",
            "Edit, proofread, and refine the article to ensure it meets the high standards of the New York Times.",
            "The article should be extremely articulate and well written. "
            "Focus on clarity, coherence, and overall quality.",
            "Ensure the article is engaging and informative.",
            "Remember: you are the final gatekeeper before the article is published.",
        ],
        add_datetime_to_instructions=True,
        markdown=True,
    )

    # Input field for the report query
    query = st.text_input("What do you want the AI journalist to write an Article on?")

    if query:
        with st.spinner("Processing..."):
            # Get the response from the assistant
            response = editor.run(query, stream=False)
            st.write(response.content)