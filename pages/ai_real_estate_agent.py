from typing import Dict, List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat,OpenAILike
from firecrawl import FirecrawlApp
import streamlit as st

class PropertyData(BaseModel):
    """Schema for property data extraction"""
    building_name: str = Field(description="Name of the building/property", alias="Building_name")
    property_type: str = Field(description="Type of property (commercial, residential, etc)", alias="Property_type")
    location_address: str = Field(description="Complete address of the property")
    price: str = Field(description="Price of the property", alias="Price")
    description: str = Field(description="Detailed description of the property", alias="Description")

class PropertiesResponse(BaseModel):
    """Schema for multiple properties response"""
    properties: List[PropertyData] = Field(description="List of property details")

class LocationData(BaseModel):
    """Schema for location price trends"""
    location: str
    price_per_sqft: float
    percent_increase: float
    rental_yield: float

class LocationsResponse(BaseModel):
    """Schema for multiple locations response"""
    locations: List[LocationData] = Field(description="List of location data points")

class FirecrawlResponse(BaseModel):
    """Schema for Firecrawl API response"""
    success: bool
    data: Dict
    status: str
    expiresAt: str

class PropertyFindingAgent:
    """Agent responsible for finding properties and providing recommendations"""
    
    def __init__(self, firecrawl_api_key: str, openai_api_key: str, model_id: str = "o3-mini"):
        self.agent = Agent(
            model=OpenAILike(id=st.session_state.openai_api_model_type, api_key=openai_api_key,base_url=st.session_state.openai_api_base_url),
            markdown=True,
            description="I am a real estate expert who helps find and analyze properties based on user preferences."
        )
        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

    def find_properties(
        self, 
        city: str,
        max_price: float,
        property_category: str = "Residential",
        property_type: str = "Flat"
    ) -> str:
        """Find and analyze properties based on user preferences"""
        formatted_location = city.lower()
        
        urls = [
            f"https://www.squareyards.com/sale/property-for-sale-in-{formatted_location}/*",
            f"https://www.99acres.com/property-in-{formatted_location}-ffid/*",
            f"https://housing.com/in/buy/{formatted_location}/{formatted_location}",
            # f"https://www.nobroker.in/property/sale/{city}/{formatted_location}",
        ]
        
        property_type_prompt = "Flats" if property_type == "Flat" else "Individual Houses"
        
        raw_response = self.firecrawl.extract(
            urls=urls,
            params={
                'prompt': f"""Extract ONLY 10 OR LESS different {property_category} {property_type_prompt} from {city} that cost less than {max_price} crores.
                
                Requirements:
                - Property Category: {property_category} properties only
                - Property Type: {property_type_prompt} only
                - Location: {city}
                - Maximum Price: {max_price} crores
                - Include complete property details with exact location
                - IMPORTANT: Return data for at least 3 different properties. MAXIMUM 10.
                - Format as a list of properties with their respective details
                """,
                'schema': PropertiesResponse.model_json_schema()
            }
        )
        
        print("Raw Property Response:", raw_response)
        
        if isinstance(raw_response, dict) and raw_response.get('success'):
            properties = raw_response['data'].get('properties', [])
        else:
            properties = []
            
        print("Processed Properties:", properties)

        
        analysis = self.agent.run(
            f"""As a real estate expert, analyze these properties and market trends:

            Properties Found in json format:
            {properties}

            **IMPORTANT INSTRUCTIONS:**
            1. ONLY analyze properties from the above JSON data that match the user's requirements:
               - Property Category: {property_category}
               - Property Type: {property_type}
               - Maximum Price: {max_price} crores
            2. DO NOT create new categories or property types
            3. From the matching properties, select 5-6 properties with prices closest to {max_price} crores

            Please provide your analysis in this format:
            
            🏠 SELECTED PROPERTIES
            • List only 5-6 best matching properties with prices closest to {max_price} crores
            • For each property include:
              - Name and Location
              - Price (with value analysis)
              - Key Features
              - Pros and Cons

            💰 BEST VALUE ANALYSIS
            • Compare the selected properties based on:
              - Price per sq ft
              - Location advantage
              - Amenities offered

            📍 LOCATION INSIGHTS
            • Specific advantages of the areas where selected properties are located

            💡 RECOMMENDATIONS
            • Top 3 properties from the selection with reasoning
            • Investment potential
            • Points to consider before purchase

            🤝 NEGOTIATION TIPS
            • Property-specific negotiation strategies

            Format your response in a clear, structured way using the above sections.
            """
        )
        
        return analysis.content

    def get_location_trends(self, city: str) -> str:
        """Get price trends for different localities in the city"""
        raw_response = self.firecrawl.extract([
            f"https://www.99acres.com/property-rates-and-price-trends-in-{city.lower()}-prffid/*"
        ], {
            'prompt': """Extract price trends data for ALL major localities in the city. 
            IMPORTANT: 
            - Return data for at least 5-10 different localities
            - Include both premium and affordable areas
            - Do not skip any locality mentioned in the source
            - Format as a list of locations with their respective data
            """,
            'schema': LocationsResponse.model_json_schema(),
        })
        
        if isinstance(raw_response, dict) and raw_response.get('success'):
            locations = raw_response['data'].get('locations', [])
    
            analysis = self.agent.run(
                f"""As a real estate expert, analyze these location price trends for {city}:

                {locations}

                Please provide:
                1. A bullet-point summary of the price trends for each location
                2. Identify the top 3 locations with:
                   - Highest price appreciation
                   - Best rental yields
                   - Best value for money
                3. Investment recommendations:
                   - Best locations for long-term investment
                   - Best locations for rental income
                   - Areas showing emerging potential
                4. Specific advice for investors based on these trends

                Format the response as follows:
                
                📊 LOCATION TRENDS SUMMARY
                • [Bullet points for each location]

                🏆 TOP PERFORMING AREAS
                • [Bullet points for best areas]

                💡 INVESTMENT INSIGHTS
                • [Bullet points with investment advice]

                🎯 RECOMMENDATIONS
                • [Bullet points with specific recommendations]
                """
            )
            
            return analysis.content
            
        return "No price trends data available"

def create_property_agent():
    """Create PropertyFindingAgent with API keys from session state"""
    if 'property_agent' not in st.session_state:
        st.session_state.property_agent = PropertyFindingAgent(
            firecrawl_api_key=st.session_state.firecrawl_api_key,
            openai_api_key=st.session_state.openai_api_key,
            model_id=st.session_state.openai_api_model_type
        )

def main():
    st.set_page_config(
        page_title="AI Real Estate Agent",
        page_icon="🏠",
        layout="wide"
    )

    with st.sidebar:
        st.title("🔑 API Configuration")
        
        # st.subheader("🤖 Model Selection")
        # model_id = st.selectbox(
        #     "Choose OpenAI Model",
        #     options=["o3-mini", "gpt-4o"],
        #     help="Select the AI model to use. Choose gpt-4o if your api doesn't have access to o3-mini"
        # )
        # st.session_state.model_id = model_id
        #
        # st.divider()
        
        st.subheader("🔐 API Keys")
        firecrawl_api_key = st.text_input(
            "Firecrawl API Key",
            type="password",
            help="Enter your Firecrawl API key",value=st.session_state.get("firecrawl_api_key")
        )
        # Get OpenAI API key from user
        openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password",
                                               value=st.session_state.get('openai_api_key'))
        openai_api_model_type = st.sidebar.text_input("OpenAI API Model Type",
                                                      value=st.session_state.get('openai_api_model_type'))
        openai_api_base_url = st.sidebar.text_input("OpenAI API Base URL",
                                                    value=st.session_state.get('openai_api_base_url'))
        st.session_state.openai_api_model_type=openai_api_model_type
        st.session_state.openai_api_base_url = openai_api_base_url

        if firecrawl_api_key and openai_api_key:
            st.session_state.firecrawl_api_key = firecrawl_api_key
            st.session_state.openai_api_key = openai_api_key
            create_property_agent()

    st.title("🏠 AI智能房地产经纪人")
    # st.info(
    #     """
    #     Welcome to the AI Real Estate Agent!
    #     Enter your search criteria below to get property recommendations
    #     and location insights.
    #     """
    # )
    st.markdown("""
    AI 房地产代理使用 Firecrawl 的 Extract 端点和 Agno AI Agent 的洞察自动进行房产搜索和市场分析。它帮助用户找到符合其标准的房产，同时提供详细的位置趋势和投资建议。该代理通过整合来自多个房地产网站的数据并提供智能分析来简化房产搜索流程。
### 特征
- **智能房产搜索**：使用 Firecrawl 的 Extract 端点在多个房地产网站上查找房产
- **多源集成**：汇总来自 99acres、Housing.com、Square Yards、Nobroker 和 MagicBricks 的数据
- **位置分析**：提供不同地区的详细价格趋势和投资见解
- **人工智能推荐**：使用 GPT 模型分析属性并提供结构化建议
- **用户友好界面**：简洁的 Streamlit UI，方便搜索房产和查看结果
- **可自定义搜索**：按城市、房产类型、类别和预算进行筛选
### 使用代理
1. **输入 API 密钥**：
   - 在侧栏中输入您的 Firecrawl 和 LLM API 密钥
   - 密钥安全地存储在会话状态中
2. **设置搜索条件**：
   - 输入城市名称
   - 选择房产类别（住宅/商业）
   - 选择房产类型（公寓/独立屋）
   - 设定最高预算（以千万卢比为单位）
3. **查看结果**：
   - 详细分析的房产推荐
   - 具有投资见解的区位趋势
   - 可扩展部分，方便阅读
### 详细功能
- **房产搜寻**：
  - 在多个房地产网站上进行搜索
  - 返回符合条件的 3-6 个属性
  - 提供详细的房产信息和分析
- **位置分析**：
  - 不同地区的价格趋势
  - 租金收益分析
  - 投资潜力评估
  - 确定表现最佳的领域
    """)

    col1, col2 = st.columns(2)
    
    with col1:
        city = st.text_input(
            "City",
            placeholder="Enter city name (e.g., Bangalore)",
            help="Enter the city where you want to search for properties"
        )
        
        property_category = st.selectbox(
            "Property Category",
            options=["Residential", "Commercial"],
            help="Select the type of property you're interested in"
        )

    with col2:
        max_price = st.number_input(
            "Maximum Price (in Crores)",
            min_value=0.1,
            max_value=100.0,
            value=5.0,
            step=0.1,
            help="Enter your maximum budget in Crores"
        )
        
        property_type = st.selectbox(
            "Property Type",
            options=["Flat", "Individual House"],
            help="Select the specific type of property"
        )

    if st.button("🔍 Start Search", use_container_width=True):
        if 'property_agent' not in st.session_state:
            st.error("⚠️ Please enter your API keys in the sidebar first!")
            return
            
        if not city:
            st.error("⚠️ Please enter a city name!")
            return
            
        try:
            with st.spinner("🔍 Searching for properties..."):
                property_results = st.session_state.property_agent.find_properties(
                    city=city,
                    max_price=max_price,
                    property_category=property_category,
                    property_type=property_type
                )
                
                st.success("✅ Property search completed!")
                
                st.subheader("🏘️ Property Recommendations")
                st.markdown(property_results)
                
                st.divider()
                
                with st.spinner("📊 Analyzing location trends..."):
                    location_trends = st.session_state.property_agent.get_location_trends(city)
                    
                    st.success("✅ Location analysis completed!")
                    
                    with st.expander("📈 Location Trends Analysis of the city"):
                        st.markdown(location_trends)
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
