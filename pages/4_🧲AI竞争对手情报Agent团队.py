import streamlit as st
from exa_py import Exa
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.models.openai import OpenAIChat,OpenAILike
from agno.tools.duckduckgo import DuckDuckGoTools
import pandas as pd
import requests
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional
import json

# Streamlit UI
# st.set_page_config(page_title="🧲 AI 竞争对手情报Agent团队", layout="wide")

# Sidebar for API keys
st.sidebar.title("API Keys")
openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
firecrawl_api_key = st.sidebar.text_input("Firecrawl API Key", type="password",
                                          value=st.session_state.get('firecrawl_api_key'))

# Add search engine selection before API keys
search_engine = st.sidebar.selectbox(
    "Select Search Endpoint",
    options=["Exa AI", "Perplexity AI - Sonar Pro"],  #
    help="Choose which AI service to use for finding competitor URLs"
)

# Show relevant API key input based on selection
if search_engine == "Perplexity AI - Sonar Pro":
    perplexity_api_key = st.sidebar.text_input("Perplexity API Key", type="password", value=st.session_state.get('perplexity_api_key'))
    # Store API keys in session state
    if openai_api_key and firecrawl_api_key and perplexity_api_key:
        st.session_state.openai_api_key = openai_api_key
        st.session_state.firecrawl_api_key = firecrawl_api_key
        st.session_state.perplexity_api_key = perplexity_api_key
    else:
        st.sidebar.warning("请输入所有必需的 API 密钥才能继续。")
else:  # Exa AI
    exa_api_key = st.sidebar.text_input("Exa API Key", type="password", value=st.session_state.get('exa_api_key'))
    # Store API keys in session state
    if openai_api_key and firecrawl_api_key and exa_api_key:
        st.session_state.openai_api_key = openai_api_key
        st.session_state.firecrawl_api_key = firecrawl_api_key
        st.session_state.exa_api_key = exa_api_key
    else:
        st.sidebar.warning("请输入所有必需的 API 密钥才能继续。")

# Main UI
st.title("🧲 AI 竞争对手情报Agent团队")
st.markdown("""
AI 竞争对手情报Agent团队是一款功能强大的竞争对手分析工具，由 Firecrawl 和 Agno 的 AI Agent 框架提供支持。此应用可帮助企业通过从竞争对手网站提取结构化数据并使用 AI 生成可操作的见解来分析其竞争对手。

## 特征

- **多Agent系统**
  - **Firecrawl Agent**：专门抓取并汇总竞争对手的网站
  - **分析Agent**：生成详细的竞争分析报告
  - **比较Agent**：在竞争对手之间创建结构化的比较
- **竞争对手发现**：
  - 使用 Exa AI 的 URL 匹配功能查找类似公司
  - 根据业务描述发现竞争对手
  - 自动提取相关竞争对手的 URL
- **综合分析**：
  - 提供结构化分析报告，内容如下：
    - 市场空白与机遇
    - 竞争对手的弱点
    - 推荐功能
    - 定价策略
    - 增长机会
    - 切实可行的建议
- **交互式分析**：用户可以输入公司网址或描述进行分析

## 用法

1. 在侧栏中输入您的 API 密钥
2. 输入：
   - 贵公司的网站网址
   - 贵公司的描述
3. 点击“分析竞争对手”生成：
   - 竞争对手对比表
   - 详细分析报告
   - 战略建议
""")
# st.info(
#     """
#     This app helps businesses analyze their competitors by extracting structured data from competitor websites and generating insights using AI.
#     - Provide a **URL** or a **description** of your company.
#     - The app will fetch competitor URLs, extract relevant information, and generate a detailed analysis report.
#     """
# )
# st.success("For better results, provide both URL and a 5-6 word description of your company!")
st.success("为了获得更好的结果，请提供 URL 和 5-6 个字的公司描述！")

# Input fields for URL and description
# url = st.text_input("Enter your company URL :")
url = st.text_input("输入公司网址：")
# description = st.text_area("Enter a description of your company (if URL is not available):")
description = st.text_area("输入公司的描述（如果没有 URL）：")

# Initialize API keys and tools
if "openai_api_key" in st.session_state and "firecrawl_api_key" in st.session_state:
    if (search_engine == "Perplexity AI - Sonar Pro" and "perplexity_api_key" in st.session_state) or \
            (search_engine == "Exa AI" and "exa_api_key" in st.session_state):

        # Initialize Exa only if selected
        if search_engine == "Exa AI":
            exa = Exa(api_key=st.session_state.get('exa_api_key'))

        firecrawl_tools = FirecrawlTools(
            api_key=st.session_state.get('firecrawl_api_key'),
            scrape=False,
            crawl=True,
            limit=5
        )

        firecrawl_agent = Agent(
            model=OpenAILike(id=st.session_state.get('openai_api_model_type'), api_key=st.session_state.get('openai_api_key'),base_url=st.session_state.get('openai_api_base_url'),
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
            tools=[firecrawl_tools, DuckDuckGoTools()],
            show_tool_calls=True,
            markdown=True
        )

        analysis_agent = Agent(
            model=OpenAILike(id=st.session_state.get('openai_api_model_type'), api_key=st.session_state.get('openai_api_key'),base_url=st.session_state.get('openai_api_base_url'),
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
            show_tool_calls=True,
            markdown=True
        )

        # New agent for comparing competitor data
        comparison_agent = Agent(
            model=OpenAILike(id=st.session_state.get('openai_api_model_type'), api_key=st.session_state.get('openai_api_key'),base_url=st.session_state.get('openai_api_base_url'),
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
            show_tool_calls=True,
            markdown=True
        )


        def get_competitor_urls(url: str = None, description: str = None) -> list[str]:
            if not url and not description:
                raise ValueError("Please provide either a URL or a description.")

            if search_engine == "Perplexity AI - Sonar Pro":
                perplexity_url = "https://api.perplexity.ai/chat/completions"

                content = "Find me 3 competitor company URLs similar to the company with "
                if url and description:
                    content += f"URL: {url} and description: {description}"
                elif url:
                    content += f"URL: {url}"
                else:
                    content += f"description: {description}"
                content += ". ONLY RESPOND WITH THE URLS, NO OTHER TEXT."

                payload = {
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Be precise and only return 3 company URLs ONLY."
                        },
                        {
                            "role": "user",
                            "content": content
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.2,
                }

                headers = {
                    "Authorization": f"Bearer {st.session_state.perplexity_api_key}",
                    "Content-Type": "application/json"
                }

                try:
                    response = requests.post(perplexity_url, json=payload, headers=headers)
                    response.raise_for_status()
                    urls = response.json()['choices'][0]['message']['content'].strip().split('\n')
                    return [url.strip() for url in urls if url.strip()]
                except Exception as e:
                    st.error(f"Error fetching competitor URLs from Perplexity: {str(e)}")
                    return []

            else:  # Exa AI
                try:
                    if url:
                        result = exa.find_similar(
                            url=url,
                            num_results=3,
                            exclude_source_domain=True,
                            category="company"
                        )
                    else:
                        result = exa.search(
                            description,
                            type="neural",
                            category="company",
                            use_autoprompt=True,
                            num_results=3
                        )
                    return [item.url for item in result.results]
                except Exception as e:
                    st.error(f"Error fetching competitor URLs from Exa: {str(e)}")
                    return []


        class CompetitorDataSchema(BaseModel):
            company_name: str = Field(description="Name of the company")
            pricing: str = Field(description="Pricing details, tiers, and plans")
            key_features: List[str] = Field(description="Main features and capabilities of the product/service")
            tech_stack: List[str] = Field(description="Technologies, frameworks, and tools used")
            marketing_focus: str = Field(description="Main marketing angles and target audience")
            customer_feedback: str = Field(description="Customer testimonials, reviews, and feedback")


        def extract_competitor_info(competitor_url: str) -> Optional[dict]:
            try:
                # Initialize FirecrawlApp with API key
                app = FirecrawlApp(api_key=st.session_state.firecrawl_api_key)

                # Add wildcard to crawl subpages
                url_pattern = f"{competitor_url}/*"

                extraction_prompt = """
                Extract detailed information about the company's offerings, including:
                - Company name and basic information
                - Pricing details, plans, and tiers
                - Key features and main capabilities
                - Technology stack and technical details
                - Marketing focus and target audience
                - Customer feedback and testimonials
                
                Analyze the entire website content to provide comprehensive information for each field.
                """

                response = app.extract(
                    [url_pattern],
                    {
                        'prompt': extraction_prompt,
                        'schema': CompetitorDataSchema.model_json_schema(),
                    }
                )

                if response.get('success') and response.get('data'):
                    extracted_info = response['data']

                    # Create JSON structure
                    competitor_json = {
                        "competitor_url": competitor_url,
                        "company_name": extracted_info.get('company_name', 'N/A'),
                        "pricing": extracted_info.get('pricing', 'N/A'),
                        "key_features": extracted_info.get('key_features', [])[:5],  # Top 5 features
                        "tech_stack": extracted_info.get('tech_stack', [])[:5],  # Top 5 tech stack items
                        "marketing_focus": extracted_info.get('marketing_focus', 'N/A'),
                        "customer_feedback": extracted_info.get('customer_feedback', 'N/A')
                    }

                    return competitor_json

                else:
                    return None

            except Exception as e:
                return None


        def generate_comparison_report(competitor_data: list) -> None:
            # Format the competitor data for the prompt
            formatted_data = json.dumps(competitor_data, indent=2)
            print(formatted_data)

            # Updated system prompt for more structured output
            system_prompt = f"""
            As an expert business analyst, analyze the following competitor data in JSON format and create a structured comparison.
            Extract and summarize the key information into concise points.

            {formatted_data}

            Return the data in a structured format with EXACTLY these columns:
            Company, Pricing, Key Features, Tech Stack, Marketing Focus, Customer Feedback

            Rules:
            1. For Company: Include company name and URL
            2. For Key Features: List top 3 most important features only
            3. For Tech Stack: List top 3 most relevant technologies only
            4. Keep all entries clear and concise
            5. Format feedback as brief quotes
            6. Return ONLY the structured data, no additional text
            """

            # Get comparison data from agent
            comparison_response = comparison_agent.run(system_prompt)

            try:
                # Split the response into lines and clean them
                table_lines = [
                    line.strip()
                    for line in comparison_response.content.split('\n')
                    if line.strip() and '|' in line
                ]

                # Extract headers (first row)
                headers = [
                    col.strip()
                    for col in table_lines[0].split('|')
                    if col.strip()
                ]

                # Extract data rows (skip header and separator rows)
                data_rows = []
                for line in table_lines[2:]:  # Skip header and separator rows
                    row_data = [
                        cell.strip()
                        for cell in line.split('|')
                        if cell.strip()
                    ]
                    if len(row_data) == len(headers):
                        data_rows.append(row_data)

                # Create DataFrame
                df = pd.DataFrame(
                    data_rows,
                    columns=headers
                )

                # Display the table
                # st.subheader("Competitor Comparison")
                st.subheader("竞争对手比较")
                st.table(df)

            except Exception as e:
                st.error(f"Error creating comparison table: {str(e)}")
                st.write("Raw comparison data for debugging:", comparison_response.content)


        def generate_analysis_report(competitor_data: list):
            # Format the competitor data for the prompt
            formatted_data = json.dumps(competitor_data, indent=2)
            print("Analysis Data:", formatted_data)  # For debugging

            report = analysis_agent.run(
                f"""Analyze the following competitor data in JSON format and identify market opportunities to improve my own company:
                
                {formatted_data}

                Tasks:
                1. Identify market gaps and opportunities based on competitor offerings
                2. Analyze competitor weaknesses that we can capitalize on
                3. Recommend unique features or capabilities we should develop
                4. Suggest pricing and positioning strategies to gain competitive advantage
                5. Outline specific growth opportunities in underserved market segments
                6. Provide actionable recommendations for product development and go-to-market strategy

                Focus on finding opportunities where we can differentiate and do better than competitors.
                Highlight any unmet customer needs or pain points we can address.
                """
            )
            return report.content


        # Run analysis when the user clicks the button
        if st.button("分析竞争对手"):
            if url or description:
                with st.spinner("Fetching competitor URLs..."):
                    competitor_urls = get_competitor_urls(url=url, description=description)
                    st.write(f"竞争对手的网址: {competitor_urls}")

                competitor_data = []
                for comp_url in competitor_urls:
                    with st.spinner(f"Analyzing Competitor: {comp_url}..."):
                        competitor_info = extract_competitor_info(comp_url)
                        if competitor_info is not None:
                            competitor_data.append(competitor_info)

                if competitor_data:
                    # Generate and display comparison report
                    with st.spinner("Generating comparison table..."):
                        generate_comparison_report(competitor_data)

                    # Generate and display final analysis report
                    with st.spinner("Generating analysis report..."):
                        analysis_report = generate_analysis_report(competitor_data)
                        # st.subheader("Competitor Analysis Report")
                        st.subheader("竞争对手分析报告")

                        st.markdown(analysis_report)

                    st.success("分析完成！")
                else:
                    # st.error("Could not extract data from any competitor URLs")
                    st.error("无法从任何竞争对手的 URL 中提取数据")
            else:
                st.error("Please provide either a URL or a description.")
