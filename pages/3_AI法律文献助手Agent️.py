'''
LegalFlow
October 08, 2023
- Maverick Reynolds
- Ian Ordonez
- James Trent
- Richard Brito 

LegalFlow is designed to connect clients with the associates of the legal firm by helping to inform clients of the services they provides as well as the next steps of the legal processes clients are involved with. LegalFlow also helps expedite administrative tasks of agents at Morgan & Morgan so that more time can be given to the associated to connect with their client.

Currenty, LegalFlow features a ChatBot designed to engage with clients who have questions regarding legal inquiries and processes for their case or general questions. LegalFlow also features a document analysis system that can classify documents into major categories based on their content. The document analysis system is designed to help Morgan & Morgan agents organize information as they continue to work with their clients.

With more time, LegalFlow will be able to provide clients with a more seamless and personalized experience with the firm's resources and associates. LegalFlow's Chatbot is available to connect with clients 24/7 and will be able to prepare preliminary documentation for clients to sign and send to the firm. We believe that incorporation of recent advancements in NLP, AI, and CV will help LegalFlow become a powerful tool for Morgan & Morgan to help clients connect with their associates and for associates to best serve the individuals and families in need.

---

App.py is the main file for the LegalFlow application. It uses dependencies from Langchain, Azure, and Streamlit to create a deployment for the Morgan & Morgan challenge at the 2023 Knight Hacks Hackathon.

Dependencies and technologies
- Langchain
- Azure AI Document Intelligence
- OpenAI GPT-3.5
- Streamlit

Github:
https://github.com/mavreyn/LegalFlow

Deployment:
http://legal-flow.streamlit.app

'''
import os
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

import streamlit as st
# from azure.ai.formrecognizer import DocumentAnalysisClient
# from azure.core.credentials import AzureKeyCredential
# from langchain.llms.openai import OpenAI
from gtts import gTTS
# from langchain import LLMChain
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
from langchain.prompts import *
from langchain_openai import OpenAI
from llama_parse import LlamaParse

# openai_api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
# azure_key = st.secrets["AZURE"]["AZURE_KEY"]
# azure_endpoint = st.secrets["AZURE"]["AZURE_ENDPOINT"]
# pip install llama-index
st.set_page_config(page_title="Legal Document Analyzer", layout="wide")

st.title("AI法律文献助手Agent️")

openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
# openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
openai_api_base_url = st.session_state.get('openai_api_base_url')


DOCUMENT_TYPES = [
    'Court Order',
    'Medical Record',
    'Medical Bill',
    'Correspondance',
    'Police Report',
    'Other'
]

def load_css():
    # os.Pat
    # __file__

    with open(os.path.join(os.path.dirname(os.path.dirname(Path(__file__))), 'code_agent/code_legal/LegalFlow/static/styles.css'), "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)



@dataclass
class Message:
    origin: Literal["human", "llm"]
    message: str


def initialize_session_state():
    if "accessibility_audio" not in st.session_state:
        st.session_state["accessibility_audio"] = False
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "conversation" not in st.session_state:
        llm = OpenAI(model_name=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url)
        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationSummaryMemory(llm=llm),
            prompt=PromptTemplate(input_variables=['history', 'input'], template="""You are 
LegalFlowAI, an AI agent at an injury law firm that is designed to help clients with any questions they may have regarding legal processes. You play a very important role in helping confort and inform our clients on questions they may have about documents, processes, and the like. 

It is important that you respond in a formal, polite, and comforting manner. Recognize that these individuals need all the resources they can get and you are here to help them. You are not a lawyer, but you are a legal assistant that can help them with any questions they may have. If they have questions that do not pertain to legality and legal process, please politefully decline to answer the question and redirect the conversation to legal topics. Please make sure to continue to interact with the client and keep asking questions to gain information; end every response with another question to the user. You can ask questions about the client's situation, the documents they have, and the like. Please make sure to keep the conversation going and make sure to ask questions that will help you understand the client's situation.
                                                          
Consider the following queries and responses between the triple backticks and how the conversation continues after each response:

```
CONVERSATION 1:

Individual: I was wondering if you knew the process for filing for a divorce?
LegalFlowAI: Of course, I would be happy to help you with that. The process for divorce depends on the state you are in. What state are you in?
Individual: I am in California.
LegalFlowAI: Great, I can help you with that. In California, you need to file a petition for divorce. You can find the form here: https://www.courts.ca.gov/documents/fl100.pdf. You will need to fill out the form and file it with the court. You will also need to serve the form to your spouse. You can find more information here: https://www.courts.ca.gov/1032.html. Are you experiencing servere domestic violence?
Individual: ...

CONVERSATION 2:
                                            
Individual: I am ready to proceed with a legal claim, What's the next step?
LegalFlowAI: I would be happy to help you with that. What kind of legal claim are you looking to proceed with?
Individual: ...
```
                                            
In addition to the above, here are some questions that clients have asked agents int he past. Be prepared to give thorough, genuine, and thoughtful conversation based on the following client texts between triple backticks:

```
- I was recently in a car accident and need an attorney
- I received my MRI results back and they were positive. What are the next steps?
- I'm experiencing pain and discomfort after the accident. What should I do?
- I have evidence of the other driver's negligence
- I have questions about the legal process for personal injury cases
- I need to understand the legal timeline for my case
- I'm experiencing emotional distress after the accident
```
                                  
Here is your conversation, continue it with the client:
```
{history}
                                  
{input}
```""")
            )


def on_click_callback():
    human_prompt = st.session_state["human_prompt"]
    # llm_response = st.session_state.conversation.run(human_prompt)
    #

    import openai
    client = openai.OpenAI(
        api_key=openai_api_key, base_url=openai_api_base_url
    )
    hs=st.session_state["result_content"]
    ps=f"""You are 
LegalFlowAI, an AI agent at an injury law firm that is designed to help clients with any questions they may have regarding legal processes. You play a very important role in helping confort and inform our clients on questions they may have about documents, processes, and the like. 

It is important that you respond in a formal, polite, and comforting manner. Recognize that these individuals need all the resources they can get and you are here to help them. You are not a lawyer, but you are a legal assistant that can help them with any questions they may have. If they have questions that do not pertain to legality and legal process, please politefully decline to answer the question and redirect the conversation to legal topics. Please make sure to continue to interact with the client and keep asking questions to gain information; end every response with another question to the user. You can ask questions about the client's situation, the documents they have, and the like. Please make sure to keep the conversation going and make sure to ask questions that will help you understand the client's situation.
                                                          
Consider the following queries and responses between the triple backticks and how the conversation continues after each response:

```
CONVERSATION 1:

Individual: I was wondering if you knew the process for filing for a divorce?
LegalFlowAI: Of course, I would be happy to help you with that. The process for divorce depends on the state you are in. What state are you in?
Individual: I am in California.
LegalFlowAI: Great, I can help you with that. In California, you need to file a petition for divorce. You can find the form here: https://www.courts.ca.gov/documents/fl100.pdf. You will need to fill out the form and file it with the court. You will also need to serve the form to your spouse. You can find more information here: https://www.courts.ca.gov/1032.html. Are you experiencing servere domestic violence?
Individual: ...

CONVERSATION 2:
                                            
Individual: I am ready to proceed with a legal claim, What's the next step?
LegalFlowAI: I would be happy to help you with that. What kind of legal claim are you looking to proceed with?
Individual: ...
```
                                            
In addition to the above, here are some questions that clients have asked agents int he past. Be prepared to give thorough, genuine, and thoughtful conversation based on the following client texts between triple backticks:

```
- I was recently in a car accident and need an attorney
- I received my MRI results back and they were positive. What are the next steps?
- I'm experiencing pain and discomfort after the accident. What should I do?
- I have evidence of the other driver's negligence
- I have questions about the legal process for personal injury cases
- I need to understand the legal timeline for my case
- I'm experiencing emotional distress after the accident
```
                                  
Here is your conversation, continue it with the client:
```
输入的pdf文件内容：```{hs}```
       
```"""
    completion = client.chat.completions.create(
        # model="gpt-4o-mini",
        model=openai_api_model_type,
        store=True,
        messages=[
            {"role": "system", "content": ps},
            {"role": "user", "content": human_prompt}
        ]
    )

    llm_response = completion.choices[0].message.content
    print(f"llm_response: {llm_response}")
    st.session_state["history"].append(
        Message("human", human_prompt)
    )
    st.session_state["history"].append(
        Message("llm", llm_response)
    )

    if st.session_state["accessibility_audio"]:
        st.sidebar.subheader('Audio Transcription')
        sound_file = BytesIO()
        tts = gTTS(llm_response, lang='en')
        tts.write_to_fp(sound_file)
        st.sidebar.audio(sound_file, format='audio/mp3')


def main():
    initialize_session_state()
    load_css()
    
    
    # Begin the Streamlit App Here
    # st.markdown("<h1 style='text-align: center; color: #ffc107;'>LegalFlow</h1>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center;'>Your assistant for document analysis & legal guidance.</h3>", unsafe_allow_html=True)
    st.markdown("""
#### **核心功能**

1. **自动文档分类**
   - 使用AI技术将法律文件智能分类为以下6类：
     - 医疗记录
     - 医疗费用单据
     - 警方报告
     - 法律协议（合同、和解书等）
     - 法院命令
     - 其他未分类文档
2. **智能法律咨询助手**
   - 支持自然语言交互，解答基础法律问题
   - 可引导用户提供必要文件或信息
3. **用户友好界面**
   - 基于Web的简洁操作平台，支持文件拖拽上传
   - 提供文本转语音（TTS）功能，增强可访问性

#### **技术实现**

- 采用**Llama Parse**技术解析文档内容，提取关键信息
- 支持常见格式（PDF、Word、扫描件等）
- 分类结果可导出，便于进一步处理

#### **适用场景**

- 快速整理案件材料（如医疗记录、警方报告）
- 自动识别医疗费用单据，便于报销或理赔对账
- 通过对话获取法律指引，减少人工咨询负担
    """)
    # Do the sidebar here
    # st.sidebar.title('语音配置')
    # use_accessibility = st.sidebar.checkbox('启用文本到语音转换功能')
    # if use_accessibility:
    #     st.session_state["accessibility_audio"] = True
    # else:
    #     st.session_state["accessibility_audio"] = False
    st.session_state["accessibility_audio"] = False
    st.sidebar.title('上传法律文件')
    file = st.sidebar.file_uploader(" ", type=["pdf", "png", "jpg", "jpeg"])

    # Add information for the file
    if file:
        with st.spinner('Analyzing your document...'):

            os.environ["LLAMA_CLOUD_API_KEY"] = "llx-FZXLhNvbI4TF094usy7482L0vrk6D5u9qsqphdJRbG58FsGv"
            parser = LlamaParse(
                result_type="text",
                language="ch_sim",
                verbose=True,
                num_workers=1,
            )

            import tempfile

            def save_uploaded_file(uploaded_file):
                """将上传的文件保存到临时目录并返回文件路径"""
                try:
                    # 创建临时目录（如果不存在）
                    temp_dir = tempfile.gettempdir()
                    os.makedirs(temp_dir, exist_ok=True)

                    # 构造文件保存路径
                    file_path = os.path.join(temp_dir, uploaded_file.name)

                    # 保存文件
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    return file_path
                except Exception as e:
                    st.error(f"保存文件时出错: {e}")
                    return None

            uploaded_file=file
            if uploaded_file is not None:
                # 显示文件信息
                st.write("文件名:", uploaded_file.name)
                st.write("文件类型:", uploaded_file.type)
                st.write("文件大小:", uploaded_file.size, "字节")

                # 保存文件到临时目录
                saved_path = save_uploaded_file(uploaded_file)

                if saved_path:
                    st.success(f"文件已成功保存到: {saved_path}")

                # src = r"C:\Users\m01216.METAX-TECH\Desktop\2025\Mar\国电投_测试资料\GBT 50796-2012 光伏发电工程验收规范.pdf"
                file=saved_path
                documents = parser.load_data(file)
                print(documents)
                docs = []
                for d in documents:
                    docs.append(d.text)
                result_content = '\n'.join(docs)
            else:
                result_content=""
            # document_analysis_client = DocumentAnalysisClient(
            #     endpoint=azure_endpoint,
            #     credential=AzureKeyCredential(azure_key)
            # )
            # poller = document_analysis_client.begin_analyze_document(
            #     "prebuilt-receipt", file
            # )
            #
            # result = poller.result()
        st.session_state["result_content"]=result_content
        st.sidebar.success('Document uploaded successfully')
    else:
        st.warning('请使用侧边栏上传文档进行分类，或继续与下面的交互')

    if file:
        st.markdown('---')
        doc_type = get_type_of_document(result_content)
        st.markdown(f"<h3 style='text-align: center;'>文章类型: {doc_type}</h3>", unsafe_allow_html=True)

    st.markdown('---')

    st.write('您好，我是AI法律文献助手Agent️，我在这里帮助您解决有关法律文件或法律程序的任何问题。请使用下面的聊天框提问。')
    st.write('')
    chat_palceholder = st.container()
    prompt_placeholder = st.form("Chat-form")

    with chat_palceholder:
        for chat in st.session_state.history:
            div = f"""
                <div class="chat-row {'llm' if chat.origin == 'llm' else 'human-bubble'}">{chat.message}</div>
            """
            st.markdown(div, unsafe_allow_html=True)

    with prompt_placeholder:
        st.text_input("开始对话", value="", key='human_prompt')
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        with c1:
            pass
        with c2:
            pass
        with c3:
            pass
        with c4:
            pass
        with c5:
            pass
        with c6:
            pass
        with c7:
            st.form_submit_button("Send", type="primary", on_click=on_click_callback)


def get_type_of_document(document_text: str) -> str:
    template = """You are an AI legal agent that is working at an injury law firm to classify certain documents. You are given a document and you need to classify it into one of the following categories:\n

    """ + "".join([f"{i+1}. {doc_type}\n" for i, doc_type in enumerate(DOCUMENT_TYPES)]) + """\nThe document you are given (by the user) has been put through an OCR system to convert it from an image to text. The OCR system is not perfect and there may be some errors in the text. The user will provide all information from the document between triple backticks in their prompt.
    
    As you walk through the document, take note of some of the information that you see. Make sure you identify the most important parts of the document. Look at important structures that you find and repeated words and phrases throughout the documents.

    Here are some observations that may help in the decision making process:
    - If a document contains "dear sir or madam" it is likely a correspondance
    - If a document has much information pertaining to physicians, Medicare, Medicaid, CT Scans, or the like, it is likely a medical record
    - If a document contains a reporting number, a date of incident, or a police officer's name, or a person record, it is likely a police report
    - If a document contains a judge's name, a case number, or a court name, it is likely a court order

    Make sure to think aloud as you make your solution. After you finish thinking aloud, put your final answer between <<< >>> as it is written above. Only use the options listed above. Here is an example of your process:
    
    
    User: ```<<<DOCUMENT INFORMATION>>>```
    AI Agent: In this document, I see information related to Federal Health 
Insurance Portability and Accountability Act (HIPAA) as well as the name of a healthcare provider. I do see the token 'correspondance' in this document, however, it is in the context of records that need to be send to the patient. I believe this document is a medical record. <<<Medical Record>>>
    
    Ensure you follow proper formatting as you use your best judgement to classify the document.
    """

    # prompt = ChatPromptTemplate.from_messages([
    #     SystemMessagePromptTemplate.from_template(template),
    #     HumanMessagePromptTemplate.from_template("```{document_text}```"),
    # ])
    #
    # chain = LLMChain(
    #     llm=OpenAI(model_name=openai_api_model_type, api_key=openai_api_key,base_url=openai_api_base_url),
    #     prompt=prompt
    # )
    # response = chain.run(document_text=document_text)

    import openai
    client = openai.OpenAI(
        api_key=openai_api_key, base_url=openai_api_base_url
    )
    completion = client.chat.completions.create(
        # model="gpt-4o-mini",
        model=openai_api_model_type,
        store=True,
        messages=[
            {"role": "system", "content": template},
            {"role": "user", "content": document_text}
        ]
    )

    response = completion.choices[0].message.content
    print(response)
    try:
        response = re.search(r'<<<(.+?)>>>', response).group(1) # Get the text between <<< >>>
    except:
        response = "".join([f'{x} ' for x in response.split()[-3:]])
    print(response)
    if response[1] == ' ':
        response = response[2:]
    
    return response


# if __name__ == '__main__':
main()
