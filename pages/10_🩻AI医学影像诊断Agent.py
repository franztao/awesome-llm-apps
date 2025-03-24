from PIL import Image as PILImage
import streamlit as st
from PIL import Image as PILImage
from agno.agent import Agent
from agno.media import Image as AgnoImage
from agno.models.openai import OpenAILike
from agno.tools.duckduckgo import DuckDuckGoTools

if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = None
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = None

with st.sidebar:
    st.title("ℹ️ API 配置")
    
    if not st.session_state.openai_api_key:
        # api_key = st.text_input(
        #     "Enter your Google API Key:",
        #     type="password"
        # )
        # st.caption(
        #     "Get your API key from [Google AI Studio]"
        #     "(https://aistudio.google.com/apikey) 🔑"
        # )
        # if api_key:
        #     st.session_state.GOOGLE_API_KEY = api_key
        #     st.success("API Key saved!")
        #     st.rerun()
        # Get LLM API Key from user
        openai_api_key = st.sidebar.text_input("LLM API Key", type="password",
                                               value=st.session_state.get('openai_api_key'))
        st.session_state.openai_api_key=openai_api_key
        openai_api_vlm_model_type = st.sidebar.text_input("VLM API Model Type",
                                                      value=st.session_state.get('openai_api_vlm_model_type'))
        st.session_state.openai_api_vlm_model_type=openai_api_vlm_model_type
        openai_api_base_url = st.sidebar.text_input("LLM API Base URL",
                                                    value=st.session_state.get('openai_api_base_url'))
        st.session_state.openai_api_base_url=openai_api_base_url

    else:
        openai_api_key = st.session_state.get('openai_api_key')
        openai_api_vlm_model_type = st.session_state.get('openai_api_vlm_model_type')
        openai_api_base_url = st.session_state.get('openai_api_base_url')
        st.success("API Key is configured")
        if st.button("🔄 Reset API Key"):
            # st.session_state.GOOGLE_API_KEY = None
            st.session_state.openai_api_key = None
            st.rerun()
    
    st.info(
        "该工具利用先进的计算机视觉和放射学专业知识，对医学成像数据进行人工智能分析。"
    )
    st.warning(
        "⚠免责声明：此工具仅用于教育和信息目的。所有分析均应由合格的医疗保健专业人员审查。请勿仅根据此分析做出医疗决定。"
    )

medical_agent = Agent(
    # model=Gemini(
    #     id="gemini-2.0-flash",
    #     # api_key=st.session_state.GOOGLE_API_KEY
    #     api_key='AIzaSyC2VJnKhQJPMmYuvN7JGvEsDyB5O8rm-Js'
    # ),
    model=OpenAILike(id=openai_api_vlm_model_type, api_key=openai_api_key,base_url=openai_api_base_url,
                system_prompt="最后输出的内容必须是中文内容呈现，不要是英文"),
    tools=[DuckDuckGoTools()],
    markdown=True
) if st.session_state.openai_api_key else None

if not medical_agent:
    st.warning("请在侧栏中配置您的 API 密钥以继续")

# Medical Analysis Query
query = """
You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the patient's medical image and structure your response as follows:

### 1. Image Type & Region
- Specify imaging modality (X-ray/MRI/CT/Ultrasound/etc.)
- Identify the patient's anatomical region and positioning
- Comment on image quality and technical adequacy

### 2. Key Findings
- List primary observations systematically
- Note any abnormalities in the patient's imaging with precise descriptions
- Include measurements and densities where relevant
- Describe location, size, shape, and characteristics
- Rate severity: Normal/Mild/Moderate/Severe

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level
- List differential diagnoses in order of likelihood
- Support each diagnosis with observed evidence from the patient's imaging
- Note any critical or urgent findings

### 4. Patient-Friendly Explanation
- Explain the findings in simple, clear language that the patient can understand
- Avoid medical jargon or provide clear definitions
- Include visual analogies if helpful
- Address common patient concerns related to these findings

### 5. Research Context
IMPORTANT: Use the DuckDuckGo search tool to:
- Find recent medical literature about similar cases
- Search for standard treatment protocols
- Provide a list of relevant medical links of them too
- Research any relevant technological advances
- Include 2-3 key references to support your analysis

Format your response using clear markdown headers and bullet points. Be concise yet thorough.
最后输出的内容必须是中文内容呈现，不要是英文
"""

st.title("🏥 医学影像诊断Agent")
st.markdown("""
- 基于LLM 的 agno 构建的医学影像诊断Agent，提供对各种扫描的医学图像的 AI 辅助分析。该Agent充当医学影像诊断专家，分析各种类型的医学图像和视频，提供详细的诊断见解和解释。
## 特征
- 综合图像分析
- 图像类型识别（X 射线、MRI、CT 扫描、超声波）
- 解剖区域检测
- 主要发现和观察
- 潜在异常检测
- 图像质量评估
- 研究与参考
## 分析组件
- **图像类型和区域**
  - 识别成像方式
  - 指定解剖区域
- **主要发现**
  - 系统地列出观察结果
  - 详细外观描述
  - 异常突出显示
- **诊断评估**
  - 潜在诊断排名
  - 鉴别诊断
  - 严重程度评估
- **患者友好的解释**
  - 简化术语
  - 详细的第一性原理解释
  - 视觉参考点
## 免责声明
此工具仅用于教育和信息目的。所有分析均应由合格的医疗保健专业人员审查。请勿仅根据此分析做出医疗决定。
""")
st.write("上传医学图像进行专业分析")

# Create containers for better organization
upload_container = st.container()
image_container = st.container()
analysis_container = st.container()

with upload_container:
    uploaded_file = st.file_uploader(
        "上传医学图像",
        type=["jpg", "jpeg", "png", "dicom"],
        help="Supported formats: JPG, JPEG, PNG, DICOM"
    )

if uploaded_file is not None:
    with image_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image = PILImage.open(uploaded_file)
            width, height = image.size
            aspect_ratio = width / height
            new_width = 500
            new_height = int(new_width / aspect_ratio)
            resized_image = image.resize((new_width, new_height))
            
            st.image(
                resized_image,
                caption="已上传医学图像",
                use_container_width=True
            )
            
            analyze_button = st.button(
                "🔍 分析图像",
                type="primary",
                use_container_width=True
            )
    
    with analysis_container:
        if analyze_button:
            with st.spinner("🔄 Analyzing image... Please wait."):
                try:
                    temp_path = "temp_resized_image.png"
                    resized_image.save(temp_path)
                    
                    # Create AgnoImage object
                    agno_image = AgnoImage(filepath=temp_path)  # Adjust if constructor differs
                    
                    # Run analysis
                    response = medical_agent.run(query, images=[agno_image])
                    st.markdown("### 📋 分析结果")
                    st.markdown("---")
                    st.markdown(response.content)
                    st.markdown("---")
                    st.caption(
                        "注意：此分析由人工智能生成，应由合格的医疗保健专业人员进行审核。"
                    )
                except Exception as e:
                    st.error(f"分析失败: {e}")
else:
    st.info("👆 请上传医学图像以开始分析")
