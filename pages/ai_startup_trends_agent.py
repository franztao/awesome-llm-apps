import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.models.anthropic import Claude
from agno.tools.newspaper4k import Newspaper4kTools
# from agno.tools import Tool
import logging

logging.basicConfig(level=logging.DEBUG)

# Setting up Streamlit app
st.title("📈 AI 初创企业趋势分析Agent")
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
topic = st.text_input("Enter the area of interest for your Startup:")
# anthropic_api_key = st.sidebar.text_input("Enter Anthropic API Key", type="password")
openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.openai_api_key)

if st.button("Generate Analysis"):
    if not openai_api_key:
        st.warning("Please enter the required API key.")
    else:
        with st.spinner("Processing your request..."):
            try:
                # Initialize Anthropic model
                # anthropic_model = Claude(id ="claude-3-5-sonnet-20240620",api_key=anthropic_api_key)
                anthropic_model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,
                           base_url=st.session_state.openai_api_base_url)
                # Define News Collector Agent - Duckduckgo_search tool enables an Agent to search the web for information.
                search_tool = DuckDuckGoTools(search=True, news=True, fixed_max_results=5)
                news_collector = Agent(
                    name="News Collector",
                    role="Collects recent news articles on the given topic",
                    tools=[search_tool],
                    model=anthropic_model,
                    instructions=["Gather latest articles on the topic"],
                    show_tool_calls=True,
                    markdown=True,
                )

                # Define Summary Writer Agent
                news_tool = Newspaper4kTools(read_article=True, include_summary=True)
                summary_writer = Agent(
                    name="Summary Writer",
                    role="Summarizes collected news articles",
                    tools=[news_tool],
                    model=anthropic_model,
                    instructions=["Provide concise summaries of the articles"],
                    show_tool_calls=True,
                    markdown=True,
                )

                # Define Trend Analyzer Agent
                trend_analyzer = Agent(
                    name="Trend Analyzer",
                    role="Analyzes trends from summaries",
                    model=anthropic_model,
                    instructions=["Identify emerging trends and startup opportunities"],
                    show_tool_calls=True,
                    markdown=True,
                )

                # The multi agent Team setup of phidata:
                agent_team = Agent(
                    team=[news_collector, summary_writer, trend_analyzer],
                    instructions=[
                        "First, search DuckDuckGo for recent news articles related to the user's specified topic.",
                        "Then, provide the collected article links to the summary writer.",
                        "Important: you must ensure that the summary writer receives all the article links to read.",
                        "Next, the summary writer will read the articles and prepare concise summaries of each.",
                        "After summarizing, the summaries will be passed to the trend analyzer.",
                        "Finally, the trend analyzer will identify emerging trends and potential startup opportunities based on the summaries provided in a detailed Report form so that any young entreprenur can get insane value reading this easily"
                    ],
                    show_tool_calls=True,
                    markdown=True,
                )

                # Executing the workflow
                # Step 1: Collect news
                news_response = news_collector.run(f"Collect recent news on {topic}")
                articles = news_response.content

                # Step 2: Summarize articles
                summary_response = summary_writer.run(f"Summarize the following articles:\n{articles}")
                summaries = summary_response.content

                # Step 3: Analyze trends
                trend_response = trend_analyzer.run(f"Analyze trends from the following summaries:\n{summaries}")
                analysis = trend_response.content

                # Display results - if incase you want to use this furthur, you can uncomment the below 2 lines to get the summaries too!
                # st.subheader("News Summaries")
                # # st.write(summaries)

                st.subheader("Trend Analysis and Potential Startup Opportunities")
                st.write(analysis)

            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Enter the topic and API keys, then click 'Generate Analysis' to start.")
