import os
import tempfile

import streamlit as st
from agno.agent import Agent
from agno.document.chunking.document import DocumentChunking
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.models.openai import OpenAILike
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.qdrant import Qdrant
from llama_cloud_services import LlamaParse


def init_session_state():
    """Initialize session state variables"""
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = None
    if 'openai_api_model_type' not in st.session_state:
        st.session_state.openai_api_model_type = None
    if 'openai_api_vlm_model_type' not in st.session_state:
        st.session_state.openai_api_vlm_model_type = None
    if 'openai_api_embedding_model_type' not in st.session_state:
        st.session_state.openai_api_embedding_model_type = None
    if 'openai_api_base_url' not in st.session_state:
        st.session_state.openai_api_base_url = None
    if 'qdrant_api_key' not in st.session_state:
        st.session_state.qdrant_api_key = None
    if 'qdrant_url' not in st.session_state:
        st.session_state.qdrant_url = None
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = None
    if 'legal_team' not in st.session_state:
        st.session_state.legal_team = None
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None
    # Add a new state variable to track processed files
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()

COLLECTION_NAME = "legal_documents"  # Define your collection name

def init_qdrant():
    """Initialize Qdrant client with configured settings."""
    if not all([st.session_state.qdrant_api_key, st.session_state.qdrant_url]):
        return None
    try:
        # Create Agno's Qdrant instance which implements VectorDb
        vector_db = Qdrant(
            collection=COLLECTION_NAME,
            url=st.session_state.qdrant_url,
            api_key=st.session_state.qdrant_api_key,
            embedder=OpenAIEmbedder(
                id=st.session_state.openai_api_embedding_model_type,
                base_url=st.session_state.openai_api_base_url,
                api_key=st.session_state.openai_api_key
            )
        )
        return vector_db
    except Exception as e:
        st.error(f"🔴 Qdrant connection failed: {str(e)}")
        return None

def process_document(uploaded_file, vector_db: Qdrant):
    """
    Process document, create embeddings and store in Qdrant vector database
    
    Args:
        uploaded_file: Streamlit uploaded file object
        vector_db (Qdrant): Initialized Qdrant instance from Agno
    
    Returns:
        PDFKnowledgeBase: Initialized knowledge base with processed documents
    """
    if not st.session_state.openai_api_key:
        raise ValueError("LLM API Key not provided")

    os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key

    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name

        os.environ["LLAMA_CLOUD_API_KEY"] = "llx-FZXLhNvbI4TF094usy7482L0vrk6D5u9qsqphdJRbG58FsGv"
        parser = LlamaParse(
            result_type="text",
            language="ch_sim",
            verbose=True,
            num_workers=1,
        )
        documents = parser.load_data(temp_file_path)
        print(documents)
        docs = []
        for d in documents:
            docs.append(d.text)
        result_content = '\n'.join(docs)

        st.info("正在加载并处理文档...")

        # Create a PDFKnowledgeBase with the vector_db
        knowledge_base = PDFKnowledgeBase(
            path=temp_file_path,  # Single string path, not a list
            vector_db=vector_db,
            reader=PDFReader(),
            chunking_strategy=DocumentChunking(
                chunk_size=1000,
                overlap=200
            )
        )

        # Load the documents into the knowledge base
        with st.spinner('📤 Loading documents into knowledge base...'):
            try:
                knowledge_base.load(recreate=True, upsert=True)
                st.success("✅ 文档存储成功！")
            except Exception as e:
                st.error(f"Error loading documents: {str(e)}")
                raise

        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except Exception:
            pass

        return knowledge_base,result_content

    except Exception as e:
        st.error(f"Document processing error: {str(e)}")
        raise Exception(f"Error processing document: {str(e)}")

def main():
    st.set_page_config(page_title="全方位服务法律Agent团队", layout="wide")
    init_session_state()

    st.title("‍⚖️ 全方位法律服务Agent团队 👨‍⚖️")
    st.markdown("""#### 核心功能

1. **专业化AI法律分析团队**
   - 由四个专业AI角色组成协同工作系统：
     1. 法律研究员：自动检索判例法规，提供带来源标注的研究报告
     2. 合同分析师：识别合同关键条款，标记风险点和义务条款
     3. 法律策略师：评估法律风险，提供应对策略建议
     4. 团队协调员：整合各角色分析，确保结论一致性
2. **全流程法律服务支持**
   - 覆盖五大业务场景：
     - 合同审查（标准/定制合同）
     - 法律案例研究
     - 业务合规审查
     - 交易风险评估
     - 定制化法律分析

#### 技术实现

- 采用多智能体(Multi-Agent)协同架构
- 集成法律数据库与互联网检索(DuckDuckGo)
- 支持文档结构化解析与条款关联分析

#### **适用场景**

- 自动生成带出处的法律备忘录
- 系统性降低合同履约风险

- 交易文件合规性自动检查
- 投资项目的法律风险量化评估
- 监管要求的自动化跟踪提示
    """)
    with st.sidebar:
        st.header("🔑 API 配置")

        openai_key = st.text_input(
            "LLM API Key",
            type="password",
            value=st.session_state.openai_api_key if st.session_state.openai_api_key else "",
            help="Enter your LLM API Key"
        )
        if openai_key:
            st.session_state.openai_api_key = openai_key

        openai_api_vlm_model_type = st.text_input(
            "VLM API Model Type",
            value=st.session_state.openai_api_vlm_model_type if st.session_state.openai_api_vlm_model_type else "",
            help="Enter your VLM API Model Type"
        )
        if openai_api_vlm_model_type:
            st.session_state.openai_api_vlm_model_type = openai_api_vlm_model_type


        openai_api_embedding_model_type = st.text_input(
            "Embedding API  Model Type",
            value=st.session_state.openai_api_embedding_model_type if st.session_state.openai_api_embedding_model_type else "",
            help="Enter your Embedding API  Model Type"
        )
        if openai_api_embedding_model_type:
            st.session_state.openai_api_embedding_model_type = openai_api_embedding_model_type

        qdrant_key = st.text_input(
            "Qdrant API Key",
            type="password",
            value=st.session_state.qdrant_api_key if st.session_state.qdrant_api_key else "",
            help="Enter your Qdrant API key"
        )
        if qdrant_key:
            st.session_state.qdrant_api_key = qdrant_key

        qdrant_url = st.text_input(
            "Qdrant URL",
            value=st.session_state.qdrant_url if st.session_state.qdrant_url else "",
            help="Enter your Qdrant instance URL"
        )
        if qdrant_url:
            st.session_state.qdrant_url = qdrant_url

        if all([st.session_state.qdrant_api_key, st.session_state.qdrant_url]):
            try:
                if not st.session_state.vector_db:
                    # Make sure we're initializing a QdrantClient here
                    st.session_state.vector_db = init_qdrant()
                    if st.session_state.vector_db:
                        st.success("Successfully connected to Qdrant!")
            except Exception as e:
                st.error(f"Failed to connect to Qdrant: {str(e)}")

        # st.divider()

    if all([st.session_state.openai_api_key, st.session_state.vector_db]):
        # st.header("📄 Document Upload")
        st.header("📄 文档上传")
        # uploaded_file = st.file_uploader("Upload Legal Document", type=['pdf'])
        uploaded_file = st.file_uploader("上传法律文档", type=['pdf'])

        if uploaded_file:
            # Check if this file has already been processed
            if uploaded_file.name not in st.session_state.processed_files:
                with st.spinner("Processing document..."):
                    try:
                        # Process the document and get the knowledge base
                        knowledge_base,result_content = process_document(uploaded_file, st.session_state.vector_db)
                        st.session_state['result_content']=result_content
                        if knowledge_base:
                            st.session_state.knowledge_base = knowledge_base
                            # Add the file to processed files
                            st.session_state.processed_files.add(uploaded_file.name)

                            # Initialize agents
                            legal_researcher = Agent(
                                name="Legal Researcher",
                                role="Legal research specialist",
                                model=OpenAILike(id=st.session_state.openai_api_vlm_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
                                tools=[DuckDuckGoTools()],
                                knowledge=st.session_state.knowledge_base,
                                search_knowledge=True,
                                instructions=[
                                    "Find and cite relevant legal cases and precedents",
                                    "Provide detailed research summaries with sources",
                                    "Reference specific sections from the uploaded document",
                                    "Always search the knowledge base for relevant information"
                                ],
                                show_tool_calls=True,
                                markdown=True
                            )

                            contract_analyst = Agent(
                                name="Contract Analyst",
                                role="Contract analysis specialist",
                                model=OpenAILike(id=st.session_state.openai_api_vlm_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
                                knowledge=st.session_state.knowledge_base,
                                search_knowledge=True,
                                instructions=[
                                    "Review contracts thoroughly",
                                    "Identify key terms and potential issues",
                                    "Reference specific clauses from the document"
                                ],
                                markdown=True
                            )

                            legal_strategist = Agent(
                                name="Legal Strategist",
                                role="Legal strategy specialist",
                                model=OpenAILike(id=st.session_state.openai_api_vlm_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
                                knowledge=st.session_state.knowledge_base,
                                search_knowledge=True,
                                instructions=[
                                    "Develop comprehensive legal strategies",
                                    "Provide actionable recommendations",
                                    "Consider both risks and opportunities"
                                ],
                                markdown=True
                            )

                            # Legal Agent Team
                            st.session_state.legal_team = Agent(
                                name="Legal Team Lead",
                                role="Legal team coordinator",
                                model=OpenAILike(id=st.session_state.openai_api_vlm_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
                                team=[legal_researcher, contract_analyst, legal_strategist],
                                knowledge=st.session_state.knowledge_base,
                                search_knowledge=True,
                                instructions=[
                                    "Coordinate analysis between team members",
                                    "Provide comprehensive responses",
                                    "Ensure all recommendations are properly sourced",
                                    "Reference specific parts of the uploaded document",
                                    "Always search the knowledge base before delegating tasks"
                                ],
                                show_tool_calls=True,
                                markdown=True
                            )

                            st.success("✅文档已处理并团队已初始化！")

                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
            else:
                # File already processed, just show a message
                # st.success("✅ Document already processed and team ready!")
                st.success("✅ 文件已处理完毕且agent准备就绪！")


        st.divider()
        # st.header("🔍 Analysis Options")
        st.header("🔍 分析选项")
        # 选择分析类型
        analysis_type = st.selectbox(
            "选择分析类型",
            [
                "Contract Review",
                "Legal Research",
                "Risk Assessment",
                "Compliance Check",
                "Custom Query"
            ]
        )
    else:
        st.warning("Please configure all API credentials to proceed")

    # Main content area
    if not all([st.session_state.openai_api_key, st.session_state.vector_db]):
        st.info("👈 Please configure your API credentials in the sidebar to begin")
    elif not uploaded_file:
        st.info("👈 请上传法律文件以开始分析")
    elif st.session_state.legal_team:
        # Create a dictionary for analysis type icons
        analysis_icons = {
            "Contract Review": "📑",
            "Legal Research": "🔍",
            "Risk Assessment": "⚠️",
            "Compliance Check": "✅",
            "Custom Query": "💭"
        }

        # Dynamic header with icon
        st.header(f"{analysis_icons[analysis_type]} {analysis_type} 分析")

        analysis_configs = {
            "Contract Review": {
                "query": "Review this contract and identify key terms, obligations, and potential issues.",
                "agents": ["Contract Analyst"],
                # "description": "Detailed contract analysis focusing on terms and obligations"
                "description": "详细分析合同条款和义务"
            },
            "Legal Research": {
                "query": "Research relevant cases and precedents related to this document.",
                "agents": ["Legal Researcher"],
                # "description": "Research on relevant legal cases and precedents"
                "description": "相关法律案例和判例研究"
            },
            "Risk Assessment": {
                "query": "Analyze potential legal risks and liabilities in this document.",
                "agents": ["Contract Analyst", "Legal Strategist"],
                # "description": "Combined risk analysis and strategic assessment"
                "description": "综合风险分析与战略评估"
            },
            "Compliance Check": {
                "query": "Check this document for regulatory compliance issues.",
                "agents": ["Legal Researcher", "Contract Analyst", "Legal Strategist"],
                # "description": "Comprehensive compliance analysis"
                "description": "全面的合规性分析"
            },
            "Custom Query": {
                "query": None,
                "agents": ["Legal Researcher", "Contract Analyst", "Legal Strategist"],
                # "description": "Custom analysis using all available agents"
                "description": "使用所有可用agent进行自定义分析"
            }
        }

        st.info(f"📋 {analysis_configs[analysis_type]['description']}")
        st.write(f"🤖 法律 AI Agents: {', '.join(analysis_configs[analysis_type]['agents'])}")  #dictionary!!

        # Replace the existing user_query section with this:
        if analysis_type == "Custom Query":
            user_query = st.text_area(
                "Enter your specific query:",
                help="Add any specific questions or points you want to analyze"
            )
        else:
            user_query = None  # Set to None for non-custom queries


        if st.button("分析"):
            if analysis_type == "Custom Query" and not user_query:
                st.warning("Please enter a query")
            else:
                with st.spinner("Analyzing document..."):
                    try:
                        # Ensure LLM API Key is set
                        os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key

                        # Combine predefined and user queries
                        result_content = st.session_state['result_content']
                        print(result_content)
                        if analysis_type != "Custom Query":

                            combined_query = f"""pdf正文:```{result_content}```
                            Using the uploaded document as reference:
                            
                            Primary Analysis Task: {analysis_configs[analysis_type]['query']}
                            Focus Areas: {', '.join(analysis_configs[analysis_type]['agents'])}
                            
                            Please search the knowledge base and provide specific references from the document.。最后输出的内容必须是中文内容呈现，不要是英文
                            """
                        else:
                            # result_content=st.session_state['result_content']
                            combined_query = f"""pdf正文:```{result_content}```
                            Using the uploaded document as reference:
                            
                            {user_query}
                            
                            Please search the knowledge base and provide specific references from the document.
                            Focus Areas: {', '.join(analysis_configs[analysis_type]['agents'])}。最后输出的内容必须是中文内容呈现，不要是英文
                            """

                        response = st.session_state.legal_team.run(combined_query)

                        # Display results in tabs
                        tabs = st.tabs(["Analysis", "Key Points", "Recommendations"])
                        print(response.content)
                        with tabs[0]:
                            st.markdown("### 详细分析")
                            if response.content:
                                st.markdown(response.content)
                            else:
                                for message in response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)

                        with tabs[1]:
                            st.markdown("### 要点")
                            key_points_response = st.session_state.legal_team.run(
                                f"""pdf正文:```{result_content}```Based on this previous analysis:    
                                {response.content}
                                
                                Please summarize the key points in bullet points.
                                Focus on insights from: {', '.join(analysis_configs[analysis_type]['agents'])}。最后输出的内容必须是中文内容呈现，不要是英文"""
                            )
                            if key_points_response.content:
                                st.markdown(key_points_response.content)
                            else:
                                for message in key_points_response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)

                        with tabs[2]:
                            st.markdown("### 建议")
                            recommendations_response = st.session_state.legal_team.run(
                                f"""pdf正文:```{result_content}```Based on this previous analysis:
                                {response.content}
                                
                                What are your key recommendations based on the analysis, the best course of action?
                                Provide specific recommendations from: {', '.join(analysis_configs[analysis_type]['agents'])}。最后输出的内容必须是中文内容呈现，不要是英文"""
                            )
                            if recommendations_response.content:
                                st.markdown(recommendations_response.content)
                            else:
                                for message in recommendations_response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)

                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
    else:
        st.info("请上传法律文件以开始分析")

if __name__ == "__main__":
    main()