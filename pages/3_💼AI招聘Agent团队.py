import json
import time
from datetime import datetime, timedelta
from typing import Literal, Tuple, Dict, Optional

import PyPDF2
import pytz
import requests
import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.tools.email import EmailTools
from phi.tools.zoom import ZoomTool
from phi.utils.log import logger
from streamlit_pdf_viewer import pdf_viewer


class CustomZoomTool(ZoomTool):
    def __init__(self, *, account_id: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None, name: str = "zoom_tool"):
        super().__init__(account_id=account_id, client_id=client_id, client_secret=client_secret, name=name)
        self.token_url = "https://zoom.us/oauth/token"
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self) -> str:
        if self.access_token and time.time() < self.token_expires_at:
            return str(self.access_token)
            
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "account_credentials", "account_id": self.account_id}

        try:
            response = requests.post(self.token_url, headers=headers, data=data, auth=(self.client_id, self.client_secret))
            response.raise_for_status()

            token_info = response.json()
            self.access_token = token_info["access_token"]
            expires_in = token_info["expires_in"]
            self.token_expires_at = time.time() + expires_in - 60

            self._set_parent_token(str(self.access_token))
            return str(self.access_token)

        except requests.RequestException as e:
            logger.error(f"Error fetching access token: {e}")
            return ""

    def _set_parent_token(self, token: str) -> None:
        """Helper method to set the token in the parent ZoomTool class"""
        if token:
            self._ZoomTool__access_token = token


# Role requirements as a constant dictionary
ROLE_REQUIREMENTS: Dict[str, str] = {
    "ai_ml_engineer": """
        所需技能：
        - Python、PyTorch/TensorFlow
        - 机器学习算法和框架
        - 深度学习和神经网络
        - 数据预处理和分析
        - MLOps 和模型部署
        - RAG、LLM、微调和快速工程
    """,

    "frontend_engineer": """
        所需技能：
        - React/Vue.js/Angular
        - HTML5、CSS3、JavaScript/TypeScript
        - 响应式设计
        - 状态管理
        - 前端测试
    """,

    "backend_engineer": """
        所需技能：
        - Python/Java/Node.js
        - REST API
        - 数据库设计和管理
        - 系统架构
        - 云服务 (AWS/GCP/Azure)
        - Kubernetes、Docker、CI/CD
    """
}


def init_session_state() -> None:
    """Initialize only necessary session state variables."""
    defaults = {
        'candidate_email': "", 'openai_api_key': "", 'resume_text': "", 'analysis_complete': False,
        'is_selected': False, 'zoom_account_id': "", 'zoom_client_id': "", 'zoom_client_secret': "",
        'email_sender': "", 'email_passkey': "", 'company_name': "", 'current_pdf': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def create_resume_analyzer() -> Agent:
    """Creates and returns a resume analysis agent."""
    if not st.session_state.openai_api_key:
        st.error("Please enter your LLM API Key first.")
        return None

    return Agent(
        model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        description="You are an expert technical recruiter who analyzes resumes.",
        instructions=[
            "Analyze the resume against the provided job requirements",
            "Be lenient with AI/ML candidates who show strong potential",
            "Consider project experience as valid experience",
            "Value hands-on experience with key technologies",
            "Return a JSON response with selection decision and feedback"
        ],
        markdown=True
    )

def create_email_agent() -> Agent:
    return Agent(
        model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        tools=[EmailTools(
            receiver_email=st.session_state.candidate_email,
            sender_email=st.session_state.email_sender,
            sender_name=st.session_state.company_name,
            sender_passkey=st.session_state.email_passkey
        )],
        description="You are a professional recruitment coordinator handling email communications.",
        instructions=[
            "Draft and send professional recruitment emails",
            "Act like a human writing an email and use all lowercase letters",
            "Maintain a friendly yet professional tone",
            "Always end emails with exactly: 'best,\nthe ai recruiting team'",
            "Never include the sender's or receiver's name in the signature",
            f"The name of the company is '{st.session_state.company_name}'"
        ],
        markdown=True,
        show_tool_calls=True
    )

def create_scheduler_agent() -> Agent:
    zoom_tools = CustomZoomTool(
        account_id=st.session_state.zoom_account_id,
        client_id=st.session_state.zoom_client_id,
        client_secret=st.session_state.zoom_client_secret
    )

    return Agent(
        name="Interview Scheduler",
        model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=st.session_state.openai_api_key,base_url=st.session_state.openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
        tools=[zoom_tools],
        description="You are an interview scheduling coordinator.",
        instructions=[
            "You are an expert at scheduling technical interviews using Zoom.",
            "Schedule interviews during business hours (9 AM - 5 PM EST)",
            "Create meetings with proper titles and descriptions",
            "Ensure all meeting details are included in responses",
            "Use ISO 8601 format for dates",
            "Handle scheduling errors gracefully"
        ],
        markdown=True,
        show_tool_calls=True
    )


def extract_text_from_pdf(pdf_file) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {str(e)}")
        return ""


def analyze_resume(
    resume_text: str,
    role: Literal["ai_ml_engineer", "frontend_engineer", "backend_engineer"],
    analyzer: Agent
) -> Tuple[bool, str]:
    try:
        response = analyzer.run(
            f"""Please analyze this resume against the following requirements and provide your response in valid JSON format:
            Role Requirements:
            {ROLE_REQUIREMENTS[role]}
            Resume Text:
            {resume_text}
            Your response must be a valid JSON object like this:
            {{
                "selected": true/false,
                "feedback": "Detailed feedback explaining the decision",
                "matching_skills": ["skill1", "skill2"],
                "missing_skills": ["skill3", "skill4"],
                "experience_level": "junior/mid/senior"
            }}
            Evaluation criteria:
            1. Match at least 70% of required skills
            2. Consider both theoretical knowledge and practical experience
            3. Value project experience and real-world applications
            4. Consider transferable skills from similar technologies
            5. Look for evidence of continuous learning and adaptability
            Important: Return ONLY the JSON object without any markdown formatting or backticks.
            """
        )

        assistant_message = next((msg.content for msg in response.messages if msg.role == 'assistant'), None)
        print(assistant_message)
        if not assistant_message:
            raise ValueError("No assistant message found in response.")

        result = json.loads(assistant_message.strip())
        if not isinstance(result, dict) or not all(k in result for k in ["selected", "feedback"]):
            raise ValueError("Invalid response format")

        return result["selected"], result["feedback"]

    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Error processing response: {str(e)}")
        return False, f"Error analyzing resume: {str(e)}"


def send_selection_email(email_agent: Agent, to_email: str, role: str) -> None:
    email_agent.run(
        f"""
        Send an email to {to_email} regarding their selection for the {role} position.
        The email should:
        1. Congratulate them on being selected
        2. Explain the next steps in the process
        3. Mention that they will receive interview details shortly
        4. The name of the company is 'AI Recruiting Team'
        """
    )


def send_rejection_email(email_agent: Agent, to_email: str, role: str, feedback: str) -> None:
    """
    Send a rejection email with constructive feedback.
    """
    email_agent.run(
        f"""
        Send an email to {to_email} regarding their application for the {role} position.
        Use this specific style:
        1. use all lowercase letters
        2. be empathetic and human
        3. mention specific feedback from: {feedback}
        4. encourage them to upskill and try again
        5. suggest some learning resources based on missing skills
        6. end the email with exactly:
           best,
           the ai recruiting team
        
        Do not include any names in the signature.
        The tone should be like a human writing a quick but thoughtful email.
        """
    )


def schedule_interview(scheduler: Agent, candidate_email: str, email_agent: Agent, role: str) -> None:
    """
    Schedule interviews during business hours (9 AM - 5 PM IST).
    """
    try:
        # Get current time in IST
        ist_tz = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist_tz)

        tomorrow_ist = current_time_ist + timedelta(days=1)
        interview_time = tomorrow_ist.replace(hour=11, minute=0, second=0, microsecond=0)
        formatted_time = interview_time.strftime('%Y-%m-%dT%H:%M:%S')

        meeting_response = scheduler.run(
            f"""Schedule a 60-minute technical interview with these specifications:
            - Title: '{role} Technical Interview'
            - Date: {formatted_time}
            - Timezone: IST (India Standard Time)
            - Attendee: {candidate_email}
            
            Important Notes:
            - The meeting must be between 9 AM - 5 PM IST
            - Use IST (UTC+5:30) timezone for all communications
            - Include timezone information in the meeting details
            """
        )

        email_agent.run(
            f"""Send an interview confirmation email with these details:
            - Role: {role} position
            - Meeting Details: {meeting_response}
            
            Important:
            - Clearly specify that the time is in IST (India Standard Time)
            - Ask the candidate to join 5 minutes early
            - Include timezone conversion link if possible
            - Ask him to be confident and not so nervous and prepare well for the interview
            """
        )
        
        st.success("面试安排成功！请查看您的电子邮件了解详情。")
        
    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        st.error("Unable to schedule interview. Please try again.")


def main() -> None:
    st.title("💼 AI 招聘Agent团队")
    st.markdown("""
    Streamlit 应用程序模拟了一支全方位服务的招聘团队，使用多个 AI Agent来自动化和简化招聘流程。每个Agent代表不同的招聘专家角色 - 从简历分析和候选人评估到面试安排和沟通 - 共同提供全面的招聘解决方案。该系统将技术招聘人员、人力资源协调员和调度专家的专业知识整合到一个有凝聚力的自动化工作流程中。
    #### 专门的人工智能Agent
    - 技术招聘Agent：分析简历并评估技术技能
    - 通讯Agent：处理专业电子邮件通信
    - 调度协调员Agent：管理面试安排和协调
    - 每位经纪人都有特定的专业知识，并相互合作，进行全面的招聘
    
    #### 端到端招聘流程
    - 自动简历筛选和分析
    - 针对具体角色的技术评估
    - 专业候选人沟通
    - 自动安排面试
    - 综合反馈系统
    
    #### 系统组件
      - **简历分析器Agent**
        - 技能匹配算法
        - 经验验证
        - 技术评估
        - 选择决策
      - **电子邮件通讯Agent**
        - 专业电子邮件起草
        - 自动通知
        - 反馈沟通
        - 后续管理
      - **面试安排员**
        - Zoom 会议协调
        - 日历管理
        - 时区处理
        - 提醒系统
      - **候选人体验**
        - 简单的上传接口
        - 实时反馈
        - 清晰的沟通
        - 简化流程
    #### 免责声明
    此工具旨在协助招聘流程，但不应完全取代人工判断。所有自动化决策都应由人工招聘人员审核以获得最终批准。
    #### 未来的增强功能
    - 与 ATS 系统集成
    - 高级候选人评分
    - 视频面试能力
    - 技能评估整合
    - 多语言支持
    """)
    init_session_state()
    with st.sidebar:
        st.header("Configuration")
        
        # OpenAI Configuration
        st.subheader("OpenAI Settings")
        api_key = st.text_input("LLM API Key", type="password", value=st.session_state.openai_api_key, help="Get your API key from platform.openai.com")
        if api_key: st.session_state.openai_api_key = api_key

        st.subheader("Zoom Settings")
        zoom_account_id = st.text_input("Zoom Account ID", type="password", value=st.session_state.zoom_account_id)
        zoom_client_id = st.text_input("Zoom Client ID", type="password", value=st.session_state.zoom_client_id)
        zoom_client_secret = st.text_input("Zoom Client Secret", type="password", value=st.session_state.zoom_client_secret)
        
        st.subheader("Email Settings")
        email_sender = st.text_input("Sender Email", value=st.session_state.email_sender, help="Email address to send from")
        email_passkey = st.text_input("Email App Password", type="password", value=st.session_state.email_passkey, help="App-specific password for email")
        company_name = st.text_input("Company Name", value=st.session_state.company_name, help="Name to use in email communications")

        if zoom_account_id: st.session_state.zoom_account_id = zoom_account_id
        if zoom_client_id: st.session_state.zoom_client_id = zoom_client_id
        if zoom_client_secret: st.session_state.zoom_client_secret = zoom_client_secret
        if email_sender: st.session_state.email_sender = email_sender
        if email_passkey: st.session_state.email_passkey = email_passkey
        if company_name: st.session_state.company_name = company_name

        required_configs = {'LLM API Key': st.session_state.openai_api_key, 'Zoom Account ID': st.session_state.zoom_account_id,
                          'Zoom Client ID': st.session_state.zoom_client_id, 'Zoom Client Secret': st.session_state.zoom_client_secret,
                          'Email Sender': st.session_state.email_sender, 'Email Password': st.session_state.email_passkey,
                          'Company Name': st.session_state.company_name}

    missing_configs = [k for k, v in required_configs.items() if not v]
    if missing_configs:
        st.warning(f"Please configure the following in the sidebar: {', '.join(missing_configs)}")
        return

    if not st.session_state.openai_api_key:
        st.warning("Please enter your LLM API Key in the sidebar to continue.")
        return

    # role = st.selectbox("Select the role you're applying for:", ["ai_ml_engineer", "frontend_engineer", "backend_engineer"])
    role = st.selectbox("选择您申请的职位：", ["ai_ml_engineer", "frontend_engineer", "backend_engineer"])
    # with st.expander("View Required Skills", expanded=True): st.markdown(ROLE_REQUIREMENTS[role])
    with st.expander("查看所需技能", expanded=True): st.markdown(ROLE_REQUIREMENTS[role])

    # Add a "New Application" button before the resume upload
    if st.button("📝 重新操作"):
        # Clear only the application-related states
        keys_to_clear = ['resume_text', 'analysis_complete', 'is_selected', 'candidate_email', 'current_pdf']
        for key in keys_to_clear:
            if key in st.session_state:
                st.session_state[key] = None if key == 'current_pdf' else ""
        st.rerun()

    resume_file = st.file_uploader("上传你的简历 (PDF)", type=["pdf"], key="resume_uploader")
    if resume_file is not None and resume_file != st.session_state.get('current_pdf'):
        st.session_state.current_pdf = resume_file
        st.session_state.resume_text = ""
        st.session_state.analysis_complete = False
        st.session_state.is_selected = False
        st.rerun()

    if resume_file:
        # st.subheader("Uploaded Resume")
        st.subheader("已经上传的简历")
        col1, col2 = st.columns([4, 1])
        
        with col1:
            import tempfile, os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(resume_file.read())
                tmp_file_path = tmp_file.name
            resume_file.seek(0)
            try: pdf_viewer(tmp_file_path)
            finally: os.unlink(tmp_file_path)
        
        with col2:
            st.download_button(label="📥 Download", data=resume_file, file_name=resume_file.name, mime="application/pdf")
        # Process the resume text
        if not st.session_state.resume_text:
            with st.spinner("Processing your resume..."):
                resume_text = extract_text_from_pdf(resume_file)
                if resume_text:
                    st.session_state.resume_text = resume_text
                    st.success("Resume processed successfully!")
                else:
                    st.error("Could not process the PDF. Please try again.")

    # Email input with session state
    email = st.text_input(
        "候选人的电子邮件地址",
        # "Candidate's email address",
        value=st.session_state.candidate_email,
        key="email_input"
    )
    st.session_state.candidate_email = email

    # Analysis and next steps
    if st.session_state.resume_text and email and not st.session_state.analysis_complete:
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing your resume..."):
                resume_analyzer = create_resume_analyzer()
                email_agent = create_email_agent()  # Create email agent here
                
                if resume_analyzer and email_agent:
                    print("DEBUG: Starting resume analysis")
                    is_selected, feedback = analyze_resume(
                        st.session_state.resume_text,
                        role,
                        resume_analyzer
                    )
                    print(f"DEBUG: Analysis complete - Selected: {is_selected}, Feedback: {feedback}")

                    if is_selected:
                        # st.success("Congratulations! Your skills match our requirements.")
                        st.success("恭喜！您的技能符合我们的要求。")
                        st.session_state.analysis_complete = True
                        st.session_state.is_selected = True
                        st.rerun()
                    else:
                        # st.warning("Unfortunately, your skills don't match our requirements.")
                        st.warning("遗憾的是，您的技能不符合我们的要求。")
                        st.write(f"反馈: {feedback}")
                        
                        # Send rejection email
                        with st.spinner("Sending feedback email..."):
                            try:
                                send_rejection_email(
                                    email_agent=email_agent,
                                    to_email=email,
                                    role=role,
                                    feedback=feedback
                                )
                                st.info("We've sent you an email with detailed feedback.")
                            except Exception as e:
                                logger.error(f"Error sending rejection email: {e}")
                                st.error("Could not send feedback email. Please try again.")

    if st.session_state.get('analysis_complete') and st.session_state.get('is_selected', False):
        # st.success("Congratulations! Your skills match our requirements.")
        st.success("恭喜！您的技能符合我们的要求。")
        # st.info("Click 'Proceed with Application' to continue with the interview process.")
        st.info("单击“继续申请”以继续面试流程。")

        
        if st.button("继续申请", key="proceed_button"):
            print("DEBUG: Proceed button clicked")  # Debug
            with st.spinner("🔄 正在处理您的申请..."):
                try:
                    print("DEBUG: Creating email agent")  # Debug
                    email_agent = create_email_agent()
                    print(f"DEBUG: Email agent created: {email_agent}")  # Debug
                    
                    print("DEBUG: Creating scheduler agent")  # Debug
                    scheduler_agent = create_scheduler_agent()
                    print(f"DEBUG: Scheduler agent created: {scheduler_agent}")  # Debug

                    # 3. Send selection email
                    with st.status("📧 正在发送确认电子邮件...", expanded=True) as status:
                        print(f"DEBUG: Attempting to send email to {st.session_state.candidate_email}")  # Debug
                        send_selection_email(
                            email_agent,
                            st.session_state.candidate_email,
                            role
                        )
                        print("DEBUG: Email sent successfully")  # Debug
                        status.update(label="✅ 确认邮件已发送！")

                    # 4. Schedule interview
                    with st.status("📅 正在安排面试...", expanded=True) as status:
                        print("DEBUG: Attempting to schedule interview")  # Debug
                        schedule_interview(
                            scheduler_agent,
                            st.session_state.candidate_email,
                            email_agent,
                            role
                        )
                        print("DEBUG: Interview scheduled successfully")  # Debug
                        # status.update(label="✅ Interview scheduled!")
                        status.update(label="✅ 已安排面试！")
                    #

                    print("DEBUG: All processes completed successfully")  # Debug
                    st.success("""
                        🎉 申请已成功处理！
                            请查看您的电子邮件以获取：
                            
                            1. 选择确认✅
                            2. 带有 Zoom 链接的面试详情🔗

                            后续步骤：
                            1. 查看职位要求
                            2. 准备技术面试
                            3. 提前 5 分钟加入面试
                    """)

                except Exception as e:
                    print(f"DEBUG: Error occurred: {str(e)}")  # Debug
                    print(f"DEBUG: Error type: {type(e)}")  # Debug
                    import traceback
                    print(f"DEBUG: Full traceback: {traceback.format_exc()}")  # Debug
                    st.error(f"An error occurred: {str(e)}")
                    st.error("Please try again or contact support.")

    # Reset button
    if st.sidebar.button("Reset Application"):
        for key in st.session_state.keys():
            if key != 'openai_api_key':
                del st.session_state[key]
        st.rerun()
# zoom heng.tao@metax-tech.com Muxi1212
if __name__ == "__main__":
    main()