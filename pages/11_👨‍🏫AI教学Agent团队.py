import os

import streamlit as st
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAILike
from agno.tools.serpapi import SerpApiTools
from agno.utils.pprint import pprint_run_response
from composio_phidata import Action, ComposioToolSet

#
# Set page configuration
st.set_page_config(page_title="👨‍🏫 AI教学Agent团队", layout="centered")

# Initialize session state for API keys and topic
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''
if 'composio_api_key' not in st.session_state:
    st.session_state['composio_api_key'] = ''
if 'serpapi_api_key' not in st.session_state:
    st.session_state['serpapi_api_key'] = ''
if 'topic' not in st.session_state:
    st.session_state['topic'] = ''

# Streamlit sidebar for API keys
with st.sidebar:
    st.title("API 配置")
    st.session_state['openai_api_key'] = st.text_input("LLM API Key", type="password",value=st.session_state.get('openai_api_key'))
    st.session_state['openai_api_model_type'] = st.sidebar.text_input("LLM API Model Type", value=st.session_state.get('openai_api_model_type'))
    st.session_state['openai_api_base_url'] = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
    st.session_state['composio_api_key'] = st.text_input("Composio API Key", type="password",value=st.session_state.get('composio_api_key'))
    st.session_state['serpapi_api_key'] = st.text_input("SerpAPI Key", type="password",value=st.session_state.get('serpapi_api_key'))
    # Add info about terminal responses
    # st.info("Note: You can also view detailed agent responses\nin your terminal after execution.")

# Validate API keys
if not st.session_state['openai_api_key'] or not st.session_state['composio_api_key'] or not st.session_state['serpapi_api_key']:
    st.error("Please enter OpenAI, Composio, and SerpAPI keys in the sidebar.")
    st.stop()

# Set the LLM API Key and Composio API key from session state
os.environ["OPENAI_API_KEY"] = st.session_state['openai_api_key']

try:
    composio_toolset = ComposioToolSet(api_key=st.session_state['composio_api_key'])
    google_docs_tool = composio_toolset.get_tools(actions=[Action.GOOGLEDOCS_CREATE_DOCUMENT])[0]
    google_docs_tool_update = composio_toolset.get_tools(actions=[Action.GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT])[0]
except Exception as e:
    st.error(f"Error initializing ComposioToolSet: {e}")
    st.stop()

# Create the Professor agent (formerly KnowledgeBuilder)
professor_agent = Agent(
    name="Professor",
    role="Research and Knowledge Specialist", 
    model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
    tools=[google_docs_tool],
    instructions=[
        "Create a comprehensive knowledge base that covers fundamental concepts, advanced topics, and current developments of the given topic.",
        "Exlain the topic from first principles first. Include key terminology, core principles, and practical applications and make it as a detailed report that anyone who's starting out can read and get maximum value out of it.",
        "Make sure it is formatted in a way that is easy to read and understand. DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
        "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create the Academic Advisor agent (formerly RoadmapArchitect)
academic_advisor_agent = Agent(
    name="Academic Advisor",
    role="Learning Path Designer",
    model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
    tools=[google_docs_tool],
    instructions=[
        "Using the knowledge base for the given topic, create a detailed learning roadmap.",
        "Break down the topic into logical subtopics and arrange them in order of progression, a detailed report of roadmap that includes all the subtopics in order to be an expert in this topic.",
        "Include estimated time commitments for each section.",
        "Present the roadmap in a clear, structured format. DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
        "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",

    ],
    show_tool_calls=True,
    markdown=True
)

# Create the Research Librarian agent (formerly ResourceCurator)
research_librarian_agent = Agent(
    name="Research Librarian",
    role="Learning Resource Specialist",
    model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
    tools=[google_docs_tool, SerpApiTools(api_key=st.session_state['serpapi_api_key']) ],
    instructions=[
        "Make a list of high-quality learning resources for the given topic.",
        "Use the SerpApi search tool to find current and relevant learning materials.",
        "Using SerpApi search tool, Include technical blogs, GitHub repositories, official documentation, video tutorials, and courses.",
        "Present the resources in a curated list with descriptions and quality assessments. DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
        "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",
    ],
    show_tool_calls=True,
    markdown=True,
)

# Create the Teaching Assistant agent (formerly PracticeDesigner)
teaching_assistant_agent = Agent(
    name="Teaching Assistant",
    role="Exercise Creator",
    model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
    tools=[google_docs_tool, SerpApiTools(api_key=st.session_state['serpapi_api_key'])],
    instructions=[
        "Create comprehensive practice materials for the given topic.",
        "Use the SerpApi search tool to find example problems and real-world applications.",
        "Include progressive exercises, quizzes, hands-on projects, and real-world application scenarios.",
        "Ensure the materials align with the roadmap progression.",
        "Provide detailed solutions and explanations for all practice materials.DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
        "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",
    ],
    show_tool_calls=True,
    markdown=True,
)

# Streamlit main UI
st.title("👨‍🏫 AI教学Agent团队")
# st.markdown("Enter a topic to generate a detailed learning path and resources")
st.markdown("""Streamlit 应用程序汇集了一支专业的 AI 教学Agent团队，他们像专业教学人员一样协作。每个Agent都充当专业教育者：课程设计师、学习路径专家、资源管理员和实践指导员 - 共同努力通过 Google Docs 创造完整的教育体验。
## 🪄 认识你的 AI 教学Agent团队
#### 🧠 教授agent
- 在 Google Docs 中创建基础知识库
- 使用适当的标题和部分来组织内容
- 包括详细解释和示例
- 输出：带有目录的综合知识库文档
#### 🗺️ 学术顾问Agent
- 在结构化的 Google Doc 中设计学习路径
- 创建渐进式里程碑标记
- 包括时间估计和先决条件
- 输出：具有清晰进展路径的视觉路线图文档
#### 📚 研究员Agent
- 将资源汇编到有组织的 Google 文档中
- 包含学术论文和教程的链接
- 添加描述和难度级别
- 输出：带有质量评级的分类资源列表
#### ✍️ 助教Agent
- 在交互式 Google Doc 中开发练习
- 创建结构化的练习部分
- 包括解决方案指南
- 输出： 完整的练习册及答案
## 如何使用？
- 在侧栏中输入您的 OpenAI API 密钥（如果未在环境中设置）
- 在侧边栏中输入您的 Composio API 密钥
- 输入你想了解的主题（例如，“Python 编程”、“机器学习”）
- 点击“生成学习计划”
- 等待Agent生成您的个性化学习计划
- 在界面中查看结果和终端输出
""")
# Add info message about Google Docs
# st.info("📝 The agents will create detailed Google Docs for each section (Professor, Academic Advisor, Research Librarian, and Teaching Assistant). The links to these documents will be displayed below after processing.")

# Query bar for topic input
st.session_state['topic'] = st.text_input("输入您想了解的主题：", placeholder="e.g., Machine Learning, LoRA, etc.")

# Start button
if st.button("开始"):
    if not st.session_state['topic']:
        st.error("Please enter a topic.")
    else:
        # Display loading animations while generating responses
        with st.spinner("Generating Knowledge Base..."):
            professor_response: RunResponse = professor_agent.run(
                f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                stream=False
            )
            
        with st.spinner("Generating Learning Roadmap..."):
            academic_advisor_response: RunResponse = academic_advisor_agent.run(
                f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                stream=False
            )
            
        with st.spinner("Curating Learning Resources..."):
            research_librarian_response: RunResponse = research_librarian_agent.run(
                f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                stream=False
            )
            
        with st.spinner("Creating Practice Materials..."):
            teaching_assistant_response: RunResponse = teaching_assistant_agent.run(
                f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                stream=False
            )

        # Extract Google Doc links from the responses
        def extract_google_doc_link(response_content):
            # Assuming the Google Doc link is embedded in the response content
            # You may need to adjust this logic based on the actual response format
            if "https://docs.google.com" in response_content:
                return response_content.split("https://docs.google.com")[1].split()[0]
            return None

        professor_doc_link = extract_google_doc_link(professor_response.content)
        academic_advisor_doc_link = extract_google_doc_link(academic_advisor_response.content)
        research_librarian_doc_link = extract_google_doc_link(research_librarian_response.content)
        teaching_assistant_doc_link = extract_google_doc_link(teaching_assistant_response.content)

        # Display Google Doc links at the top of the Streamlit UI
        st.markdown("### 文档链接:")
        if professor_doc_link:
            st.markdown(f"- **Professor Document:** [View Document](https://docs.google.com{professor_doc_link})")
        if academic_advisor_doc_link:
            st.markdown(f"- **Academic Advisor Document:** [View Document](https://docs.google.com{academic_advisor_doc_link})")
        if research_librarian_doc_link:
            st.markdown(f"- **Research Librarian Document:** [View Document](https://docs.google.com{research_librarian_doc_link})")
        if teaching_assistant_doc_link:
            st.markdown(f"- **Teaching Assistant Document:** [View Document](https://docs.google.com{teaching_assistant_doc_link})")

        # Display responses in the Streamlit UI using pprint_run_response
        st.markdown("### 教授agent Response:")
        st.markdown(professor_response.content)
        pprint_run_response(professor_response, markdown=True)
        st.divider()
        
        st.markdown("### 学术顾问Agent Response:")
        st.markdown(academic_advisor_response.content)
        pprint_run_response(academic_advisor_response, markdown=True)
        st.divider()

        st.markdown("### 研究员Agent Response:")
        st.markdown(research_librarian_response.content)
        pprint_run_response(research_librarian_response, markdown=True)
        st.divider()

        st.markdown("### 助教Agent Response:")
        st.markdown(teaching_assistant_response.content)
        pprint_run_response(teaching_assistant_response, markdown=True)
        st.divider()
# Information about the agents
st.markdown("---")
st.markdown("### 关于Agents:")
st.markdown("""
- **教授**：研究主题并创建详细的知识库。
- **学术顾问**：为主题设计结构化的学习路线图。
- **研究员**：策划高质量的学习资源。
- **助教**：创建练习材料、练习和项目。
""")
