import os
from typing import Dict, Any

import streamlit as st
from PIL import Image
from agno.agent import Agent
# from agno.models.google import Gemini
from agno.models.openai import OpenAILike
from e2b_code_interpreter import Sandbox


def initialize_session_state() -> None:
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''
    # if 'gemini_key' not in st.session_state:
    #     st.session_state.gemini_key = ''
    if 'openai_api_model_type' not in st.session_state:
        st.session_state.openai_api_model_type = None
    if 'openai_api_vlm_model_type' not in st.session_state:
        st.session_state.openai_api_vlm_model_type = None
    if 'openai_api_embedding_model_type' not in st.session_state:
        st.session_state.openai_api_embedding_model_type = None
    if 'openai_api_base_url' not in st.session_state:
        st.session_state.openai_api_base_url = None
    if 'e2b_key' not in st.session_state:
        st.session_state.e2b_key = ''
    if 'sandbox' not in st.session_state:
        st.session_state.sandbox = None

def setup_sidebar() -> None:
    with st.sidebar:
        st.title("API Configuration")
        st.session_state.openai_api_key = st.sidebar.text_input("LLM API Key", type="password",
                                               value=st.session_state.get('openai_api_key'))
        st.session_state.openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                                      value=st.session_state.get('openai_api_model_type'))
        st.session_state.openai_api_vlm_model_type = st.sidebar.text_input("VLM API Model Type",
                                                      value=st.session_state.get('openai_api_vlm_model_type'))
        st.session_state.openai_api_base_url = st.sidebar.text_input("LLM API Base URL",
                                                    value=st.session_state.get('openai_api_base_url'))
        st.session_state.e2b_key = st.text_input("E2B API Key",
                                                value=st.session_state.e2b_key,
                                                type="password")

def create_agents() -> tuple[Agent, Agent, Agent]:
    vision_agent = Agent(
        model=OpenAILike(id=st.session_state.openai_api_vlm_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        markdown=True
    )

    coding_agent = Agent(
        model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
            system_prompt="""You are an expert Python programmer. You will receive coding problems similar to LeetCode questions, 
            which may include problem statements, sample inputs, and examples. Your task is to:
            1. Analyze the problem carefully and Optimally with best possible time and space complexities.
            2. Write clean, efficient Python code to solve it
            3. Include proper documentation and type hints
            4. The code will be executed in an e2b sandbox environment
            Please ensure your code is complete and handles edge cases appropriately.最后输出的内容必须是中文内容呈现，不要是英文""")
        ,
        markdown=True
    )
    
    execution_agent = Agent(
        model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
            system_prompt="""You are an expert at executing Python code in sandbox environments.
            Your task is to:
            1. Take the provided Python code
            2. Execute it in the e2b sandbox
            3. Format and explain the results clearly
            4. Handle any execution errors gracefully
            Always ensure proper error handling and clear output formatting.最后输出的内容必须是中文内容呈现，不要是英文"""
        ),
        markdown=True
    )
    
    return vision_agent, coding_agent, execution_agent

def initialize_sandbox() -> None:
    try:
        if st.session_state.sandbox:
            try:
                st.session_state.sandbox.close()
            except:
                pass
        os.environ['E2B_API_KEY'] = st.session_state.e2b_key
        # Initialize sandbox with 60 second timeout
        st.session_state.sandbox = Sandbox(timeout=60)
    except Exception as e:
        st.error(f"Failed to initialize sandbox: {str(e)}")
        st.session_state.sandbox = None

def run_code_in_sandbox(code: str) -> Dict[str, Any]:
    if not st.session_state.sandbox:
        initialize_sandbox()
    
    execution = st.session_state.sandbox.run_code(code)
    return {
        "logs": execution.logs,
        "files": st.session_state.sandbox.files.list("/")
    }

def process_image_with_gemini(vision_agent: Agent, image: Image) -> str:
    prompt = """Analyze this image and extract any coding problem or code snippet shown. 
    Describe it in clear natural language, including any:
    1. Problem statement
    2. Input/output examples
    3. Constraints or requirements
    Format it as a proper coding problem description."""
    
    # Save image to a temporary file
    temp_path = "temp_image.png"
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(temp_path, format="PNG")
        
        # Read the file and create image data
        with open(temp_path, 'rb') as img_file:
            img_bytes = img_file.read()
            
        # Pass image to Gemini
        response = vision_agent.run(
            prompt,
            images=[{"filepath": temp_path}]  # Use filepath instead of content
        )
        return response.content
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return "Failed to process the image. Please try again or use text input instead."
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def execute_code_with_agent(execution_agent: Agent, code: str, sandbox: Sandbox) -> str:
    try:
        # Set timeout to 30 seconds for code execution
        sandbox.set_timeout(30)
        execution = sandbox.run_code(code)
        
        # Handle execution errors
        if execution.error:
            if "TimeoutException" in str(execution.error):
                return "⚠️ Execution Timeout: The code took too long to execute (>30 seconds). Please optimize your solution or try a smaller input."
            
            error_prompt = f"""The code execution resulted in an error:
            Error: {execution.error}
            
            Please analyze the error and provide a clear explanation of what went wrong."""
            response = execution_agent.run(error_prompt)
            return f"⚠️ Execution Error:\n{response.content}"
        
        # Get files list safely
        try:
            files = sandbox.files.list("/")
        except:
            files = []
        
        prompt = f"""Here is the code execution result:
        Logs: {execution.logs}
        Files: {str(files)}
        
        Please provide a clear explanation of the results and any outputs."""
        
        response = execution_agent.run(prompt)
        return response.content
    except Exception as e:
        # Reinitialize sandbox on error
        try:
            initialize_sandbox()
        except:
            pass
        return f"⚠️ Sandbox Error: {str(e)}"

def main() -> None:
    st.title("💻 多模态 AI 编码Agent团队")
    st.markdown("""
    一款由 AI 驱动的 Streamlit 应用程序，可充当您的个人编码助手，由基于LLM构建的多个Agent提供支持。您还可以上传编码问题的图像或用文字描述它，AI Agent将进行分析、生成最佳解决方案并在沙盒环境中执行它。
## 特征
#### 多模态问题输入
- 上传编码问题图片（支持PNG，JPG，JPEG）
- 自然语言中的类型问题
- 从图像中自动提取问题
- 交互式问题处理
#### 智能代码生成
- 具有最佳时间/空间复杂度的最佳解决方案生成
- 干净、有文档记录的 Python 代码输出
- 类型提示和适当的文档
- 边缘情况处理
#### 安全代码执行
- 沙盒代码执行环境
- 实时执行结果
- 错误处理和解释
- 30 秒执行超时保护
#### 多Agent架构
- 用于图像处理的 Vision Agent
- 用于生成解决方案的编码Agent
- 执行Agent用于代码运行和结果分析
- 用于安全代码执行的 E2B 沙盒
## 用法
1. 上传编码问题的图片或输入问题描述
2. 点击“生成并执行解决方案”
3. 查看生成的解决方案及其完整文档
4. 查看执行结果和任何生成的文件
5. 检查任何错误消息或执行超时
    """)
    # Add timeout info in sidebar
    initialize_session_state()
    setup_sidebar()
    with st.sidebar:
        st.info("⏱️ 代码执行超时：30 秒")
    
    # Check all required API keys
    if not (st.session_state.openai_api_key and 
            #st.session_state.gemini_key and
            st.session_state.e2b_key):
        st.warning("Please enter all required API keys in the sidebar.")
        return
    
    vision_agent, coding_agent, execution_agent = create_agents()
    
    # Clean, single-column layout
    uploaded_image = st.file_uploader(
        "上传你的有关编码问题的图片（可选）",
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    
    user_query = st.text_area(
        "或者在这里输入你的编码问题：",
        placeholder="Example: 编写一个函数来计算两个数字之和。包括输入/输出示例。",
        height=100
    )
    
    # Process button
    if st.button("生成并执行解决方案", type="primary"):
        if uploaded_image and not user_query:
            # Process image with Gemini
            with st.spinner("Processing image..."):
                try:
                    # Save uploaded file to temporary location
                    image = Image.open(uploaded_image)
                    extracted_query = process_image_with_gemini(vision_agent, image)
                    
                    if extracted_query.startswith("Failed to process"):
                        st.error(extracted_query)
                        return
                    
                    st.info("📝 Extracted Problem:")
                    st.write(extracted_query)
                    
                    # Pass extracted query to coding agent
                    with st.spinner("Generating solution..."):
                        response = coding_agent.run(extracted_query)
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    return
                
        elif user_query and not uploaded_image:
            # Direct text input processing
            with st.spinner("Generating solution..."):
                response = coding_agent.run(user_query)
                
        elif user_query and uploaded_image:
            st.error("Please use either image upload OR text input, not both.")
            return
        else:
            st.warning("Please provide either an image or text description of your coding problem.")
            return
        
        # Display and execute solution
        if 'response' in locals():
            st.divider()
            st.subheader("💻 解决方案")
            
            # Extract code from markdown response
            code_blocks = response.content.split("```python")
            if len(code_blocks) > 1:
                code = code_blocks[1].split("```")[0].strip()
                
                # Display the code
                st.code(code, language="python")
                
                # Execute code with execution agent
                with st.spinner("Executing code..."):
                    # Always initialize a fresh sandbox for each execution
                    initialize_sandbox()
                    
                    if st.session_state.sandbox:
                        execution_results = execute_code_with_agent(
                            execution_agent,
                            code,
                            st.session_state.sandbox
                        )
                        
                        # Display execution results
                        st.divider()
                        st.subheader("🚀 执行结果")
                        st.markdown(execution_results)
                        
                        # Try to display files if available
                        try:
                            files = st.session_state.sandbox.files.list("/")
                            if files:
                                st.markdown("📁 **Generated Files:**")
                                st.json(files)
                        except:
                            pass

if __name__ == "__main__":
    main()
