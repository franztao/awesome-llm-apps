import warnings
from io import StringIO

import streamlit as st
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from streamlit_extras.stylable_container import stylable_container

warnings.filterwarnings("ignore")

def main_conversationalAI():

    # Streamlit Page Setup
    # st.set_page_config(layout="wide")
    st.title("在线RAG法律咨询Agent")
    st.markdown("""#### **核心功能**

1. **精准法律信息查询**
   - 基于AI技术自动识别用户问题类型，提供两种检索方式：
     - **内部数据库检索**：从已整理的法律文档库中匹配相关内容
     - **网络补充检索**：当内部数据不足时，自动获取最新公开法律信息
2. **可靠性保障机制**
   - 多重校验流程确保答案准确性：
     1. 内容相关性验证
     2. 逻辑一致性检查
     3. 自动修正低质量回答

#### **技术实现**

- 采用**自适应RAG算法**（检索增强生成技术）
- 数据存储于专业向量数据库（ChromaDB），支持快速检索
- 可对接权威法律数据库和网络资源（Tavily）

#### **适用场景**

  - 快速获取判例、法规条文
  - 自动校验法律文书的准确性
  - 实时查询财税法规更新
  - 辅助合规性审查
    """)

    openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
    openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                                  value=st.session_state.get('openai_api_model_type'))
    # openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
    openai_api_base_url =st.session_state.get('openai_api_base_url')

    # Defining Streamlit Session Variables
    if 'doc_names' not in st.session_state:
        st.session_state.doc_names = []
    if 'uploaded_docs' not in st.session_state:
        st.session_state.uploaded_docs = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "client" not in st.session_state:
        pass
        # st.session_state.client = weaviate.Client(embedded_options = EmbeddedOptions())
    if "conversational_rag_chain" not in st.session_state:
        st.session_state.conversational_rag_chain = ""
    if "chunks" not in st.session_state:
        st.session_state.chunks = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = ""
    if "store" not in st.session_state:
        st.session_state.store = {}

    # Function for retreiving chat history
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in st.session_state.store:
            st.session_state.store[session_id] = ChatMessageHistory()
        return st.session_state.store[session_id]

    # Defining constants
    # OpenAI(model_name=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url)
    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    llm = ChatOpenAI(model_name=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url)

    # Contextualizing question using chat history
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages([("system", contextualize_q_system_prompt),MessagesPlaceholder("chat_history"),("human", "{input}"),])

    # Control prompt that answers the question
    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, recommend questions that are more relevant.\
    Use three sentences maximum and keep the answer concise.\
    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages([("system", qa_system_prompt),MessagesPlaceholder("chat_history"),("human", "{input}"),])
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # st.markdown("<h1 style='text-align: center; color: black;'>Semantic Search using GPT 3.5</h1>", unsafe_allow_html=True)
    # st.markdown(
    #     """
    #     <style>
    #         section[data-testid="stSidebar"] {
    #             width: 900px !important; # Set the width to your desired value
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )

    # Displaying all messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # If New file is uploaded Then
    uploaded_file = st.sidebar.file_uploader("上传文件")
    if uploaded_file is not None and uploaded_file.name not in st.session_state.doc_names:

        # Extracting text from the document in the form of strings
        stringio=StringIO(uploaded_file.getvalue().decode('utf-8'))
        read_data=stringio.read()

        # Storing document data
        if uploaded_file.name not in st.session_state.doc_names:
            st.session_state.uploaded_docs.append(read_data)
            st.session_state.doc_names.append(uploaded_file.name)

        # For every unique document uplaoded, the contents are chunked and the vectorstore is updated
        split_text = text_splitter.split_text(read_data)
        # st.session_state.chunks += [Document(page_content=split_text[x], metadata={"pId":x,"docName":uploaded_file.name}) for x in range(len(split_text))]
        st.session_state.chunks += [split_text[x] for x in range(len(split_text))]

        # st.session_state.vectorstore = Weaviate.from_documents(client = st.session_state.client,documents = st.session_state.chunks,embedding = OpenAIEmbeddings(),by_text = False)
        # retriever = st.session_state.vectorstore.as_retriever()

        from langchain.retrievers import BM25Retriever
        # from langchain.schema import Document

        # 准备文档数据（可以是字符串列表或 Document 对象列表）
        # documents = [
        #     "苹果是一种水果",
        #     "香蕉是一种热带水果",
        #     "汽车是一种交通工具",
        #     "Python是一种编程语言"
        # ]

        # 方法1：直接传入文本列表
        retriever = BM25Retriever.from_texts(st.session_state.chunks)


        # Updating rag chain after every upload
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        st.session_state.conversational_rag_chain = RunnableWithMessageHistory(rag_chain,get_session_history,input_messages_key="input",history_messages_key="chat_history",output_messages_key="answer",)
        print('st.session_state.conversational_rag_chain')
        print(st.session_state.conversational_rag_chain)

    # Printing unique list of document names
    st.sidebar.subheader("已经上传的文件列表")
    for i in range(len(st.session_state.doc_names)):
        with st.sidebar:
            st.subheader(str(i+1)+") "+st.session_state.doc_names[i].split(".")[0])

    # Sidebar for getting document data on entering a query
    with st.sidebar:
        # Enter Query
        text_search = st.text_input("通过查询搜索相关文档", value="")
    if text_search != "":
        # Langchain Semantic Similarity
        docs = st.session_state.vectorstore.similarity_search(text_search, k=3)
        # Printing results
        for i in range(3):
            with st.sidebar:
                Page1 = st.container(border=True)
                Page1 = stylable_container(key="Page1", css_styles=""" {box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 15px;}""")
                Page1.write(str(i+1)+". Doc Name - "+ docs[i].metadata['docName'] + ",  \t\t\t Chunk ID - "+ str(docs[i].metadata['pId']))
                Page1.write("Chunk: "+ docs[i].page_content)

    # User text input in the chat
    if prompt := st.chat_input("输入对话"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generating reponse from the rag chain pipeline using chat history
        with st.chat_message("assistant"):
            response = st.session_state.conversational_rag_chain.invoke({"input": st.session_state.messages[-1]['content']},config={"configurable": {"session_id": "abc123"}})["answer"]
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})



