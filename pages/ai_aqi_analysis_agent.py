from typing import Dict, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat, OpenAILike
from firecrawl import FirecrawlApp
import streamlit as st

class AQIResponse(BaseModel):
    success: bool
    data: Dict[str, float]
    status: str
    expiresAt: str

class ExtractSchema(BaseModel):
    aqi: float = Field(description="Air Quality Index")
    temperature: float = Field(description="Temperature in degrees Celsius")
    humidity: float = Field(description="Humidity percentage")
    wind_speed: float = Field(description="Wind speed in kilometers per hour")
    pm25: float = Field(description="Particulate Matter 2.5 micrometers")
    pm10: float = Field(description="Particulate Matter 10 micrometers")
    co: float = Field(description="Carbon Monoxide level")

@dataclass
class UserInput:
    city: str
    state: str
    country: str
    medical_conditions: Optional[str]
    planned_activity: str

class AQIAnalyzer:
    
    def __init__(self, firecrawl_key: str) -> None:
        self.firecrawl = FirecrawlApp(api_key=firecrawl_key)
    
    def _format_url(self, country: str, state: str, city: str) -> str:
        """Format URL based on location, handling cases with and without state"""
        country_clean = country.lower().replace(' ', '-')
        city_clean = city.lower().replace(' ', '-')
        
        if not state or state.lower() == 'none':
            return f"https://www.aqi.in/dashboard/{country_clean}/{city_clean}"
        
        state_clean = state.lower().replace(' ', '-')
        return f"https://www.aqi.in/dashboard/{country_clean}/{state_clean}/{city_clean}"
    
    def fetch_aqi_data(self, city: str, state: str, country: str) -> Dict[str, float]:
        """Fetch AQI data using Firecrawl"""
        try:
            url = self._format_url(country, state, city)
            st.info(f"Accessing URL: {url}")  # Display URL being accessed
            
            response = self.firecrawl.extract(
                urls=[f"{url}/*"],
                params={
                    'prompt': 'Extract the current real-time AQI, temperature, humidity, wind speed, PM2.5, PM10, and CO levels from the page. Also extract the timestamp of the data.',
                    'schema': ExtractSchema.model_json_schema()
                }
            )
            
            aqi_response = AQIResponse(**response)
            if not aqi_response.success:
                raise ValueError(f"Failed to fetch AQI data: {aqi_response.status}")
            
            with st.expander("📦 Raw AQI Data", expanded=True):
                st.json({
                    "url_accessed": url,
                    "timestamp": aqi_response.expiresAt,
                    "data": aqi_response.data
                })
                
                st.warning("""
                    ⚠️ Note: The data shown may not match real-time values on the website. 
                    This could be due to:
                    - Cached data in Firecrawl
                    - Rate limiting
                    - Website updates not being captured
                    
                    Consider refreshing or checking the website directly for real-time values.
                """)
                
            return aqi_response.data
            
        except Exception as e:
            st.error(f"Error fetching AQI data: {str(e)}")
            return {
                'aqi': 0,
                'temperature': 0,
                'humidity': 0,
                'wind_speed': 0,
                'pm25': 0,
                'pm10': 0,
                'co': 0
            }

class HealthRecommendationAgent:
    
    def __init__(self, openai_key) -> None:
        self.agent = Agent(
            model=OpenAILike(
                id=openai_key['openai_api_model_type'],
                name="Health Recommendation Agent",
                api_key=openai_key['openai'],
                base_url=openai_key['openai_api_base_url']
            )
        )


    def get_recommendations(
        self,
        aqi_data: Dict[str, float],
        user_input: UserInput
    ) -> str:
        prompt = self._create_prompt(aqi_data, user_input)
        response = self.agent.run(prompt)
        return response.content
    
    def _create_prompt(self, aqi_data: Dict[str, float], user_input: UserInput) -> str:
        return f"""
        Based on the following air quality conditions in {user_input.city}, {user_input.state}, {user_input.country}:
        - Overall AQI: {aqi_data['aqi']}
        - PM2.5 Level: {aqi_data['pm25']} µg/m³
        - PM10 Level: {aqi_data['pm10']} µg/m³
        - CO Level: {aqi_data['co']} ppb
        
        Weather conditions:
        - Temperature: {aqi_data['temperature']}°C
        - Humidity: {aqi_data['humidity']}%
        - Wind Speed: {aqi_data['wind_speed']} km/h
        
        User's Context:
        - Medical Conditions: {user_input.medical_conditions or 'None'}
        - Planned Activity: {user_input.planned_activity}
        **Comprehensive Health Recommendations:**
        1. **Impact of Current Air Quality on Health:**
        2. **Necessary Safety Precautions for Planned Activity:**
        3. **Advisability of Planned Activity:**
        4. **Best Time to Conduct the Activity:**
        """

def analyze_conditions(
    user_input: UserInput,
    api_keys: Dict[str, str]
) -> str:
    aqi_analyzer = AQIAnalyzer(firecrawl_key=api_keys['firecrawl'])
    health_agent = HealthRecommendationAgent(openai_key=api_keys)
    
    aqi_data = aqi_analyzer.fetch_aqi_data(
        city=user_input.city,
        state=user_input.state,
        country=user_input.country
    )
    
    return health_agent.get_recommendations(aqi_data, user_input)

def initialize_session_state():
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {
            'firecrawl': '',
            'openai': ''
        }

def setup_page():
    st.set_page_config(
        page_title="AQI Analysis Agent",
        page_icon="🌍",
        layout="wide"
    )
    
    st.title("🌍 AQI 分析代理")
    # st.info("Get personalized health recommendations based on air quality conditions.")
    st.markdown("""
    AQI 分析代理是一款功能强大的空气质量监测和健康建议工具，由 Firecrawl 和 Agno 的 AI Agent 框架提供支持。该应用通过分析实时空气质量数据并提供个性化的健康建议，帮助用户做出明智的户外活动决定。
## 特征
- **多代理系统**
  - **AQI 分析器**：获取并处理实时空气质量数据
  - **健康推荐代理**：生成个性化的健康建议
- **空气质量指标**：
  - 总体空气质量指数 (AQI)
  - 颗粒物（PM2.5 和 PM10）
  - 一氧化碳（CO）水平
  - 温度
  - 湿度
  - 风速
- **综合分析**：
  - 实时数据可视化
  - 健康影响评估
  - 活动安全建议
  - 户外活动最佳时间建议
  - 天气状况相关性
- **互动功能**：
  - 基于位置的分析
  - 健康状况考虑
  - 针对特定活动的建议
  - 可下载的报告
  - 快速测试的示例查询
## 用法
1. 在 API 配置部分输入您的 API 密钥
2. 输入位置详细信息：
   - 城市名称
   - 州（联邦属地/美国城市可选）
   - 国家
3. 提供个人信息：
   - 医疗状况（可选）
   - 有计划的户外活动
4. 点击“分析并获取建议”可获得：
   - 当前空气质量数据
   - 健康影响分析
   - 活动安全建议
5. 尝试示例查询以进行快速测试
## 注意
空气质量数据是使用 Firecrawl 的网页抓取功能获取的。由于缓存和速率限制，数据可能并不总是与网站上的实时值相匹配。为了获得最准确的实时数据，请考虑直接检查源网站。
    """)
def render_sidebar():
    """Render sidebar with API configuration"""
    with st.sidebar:
        st.header("🔑 API Configuration")
        
        new_firecrawl_key = st.text_input(
            "Firecrawl API Key",
            type="password",
            value=st.session_state.get('firecrawl_api_key') if st.session_state.get('firecrawl_api_key') else st.session_state.api_keys['firecrawl'],
            help="Enter your Firecrawl API key"
        )
        new_openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_api_key') if st.session_state.get('openai_api_key') else st.session_state.api_keys['openai'],
            help="Enter your OpenAI API key"
        )
        # Get OpenAI API key from user
        # openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password",
        #                                        value=st.session_state.get('openai_api_key'))
        openai_api_model_type = st.sidebar.text_input("OpenAI API Model Type",
                                                      value=st.session_state.get('openai_api_model_type'))
        openai_api_base_url = st.sidebar.text_input("OpenAI API Base URL",
                                                    value=st.session_state.get('openai_api_base_url'))
        
        if (new_firecrawl_key and new_openai_key and
            (new_firecrawl_key != st.session_state.api_keys['firecrawl'] or 
             new_openai_key != st.session_state.api_keys['openai'])):
            st.session_state.api_keys.update({
                'firecrawl': new_firecrawl_key,
                'openai': new_openai_key,
                'openai_api_model_type':openai_api_model_type,
                'openai_api_base_url':openai_api_base_url
            })
            st.success("✅ API keys updated!")

def render_main_content():
    st.header("📍 Location Details")
    col1, col2 = st.columns(2)
    
    with col1:
        city = st.text_input("City", placeholder="e.g., Mumbai")
        state = st.text_input("State", placeholder="If it's a Union Territory or a city in the US, leave it blank")
        country = st.text_input("Country", value="India", placeholder="United States")
    
    with col2:
        st.header("👤 Personal Details")
        medical_conditions = st.text_area(
            "Medical Conditions (optional)",
            placeholder="e.g., asthma, allergies"
        )
        planned_activity = st.text_area(
            "Planned Activity",
            placeholder="e.g., morning jog for 2 hours"
        )
    
    return UserInput(
        city=city,
        state=state,
        country=country,
        medical_conditions=medical_conditions,
        planned_activity=planned_activity
    )

def main():
    """Main application entry point"""
    initialize_session_state()
    setup_page()
    render_sidebar()
    user_input = render_main_content()
    
    result = None
    
    if st.button("🔍 Analyze & Get Recommendations"):
        if not all([user_input.city, user_input.planned_activity]):
            st.error("Please fill in all required fields (state and medical conditions are optional)")
        elif not all(st.session_state.api_keys.values()):
            st.error("Please provide both API keys in the sidebar")
        else:
            try:
                with st.spinner("🔄 Analyzing conditions..."):
                    result = analyze_conditions(
                        user_input=user_input,
                        api_keys=st.session_state.api_keys
                    )
                    st.success("✅ Analysis completed!")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if result:
        st.markdown("### 📦 Recommendations")
        st.markdown(result)
        
        st.download_button(
            "💾 Download Recommendations",
            data=result,
            file_name=f"aqi_recommendations_{user_input.city}_{user_input.state}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()