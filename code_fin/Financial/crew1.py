from crewai import Agent, Task, Crew, Process
from langchain.llms import Ollama
from ..Financial.tools.yf_tech_analysis_tool import yf_tech_analysis
from ..Financial.tools.yf_fundamental_analysis_tool import yf_fundamental_analysis
from ..Financial.tools.sentiment_analysis_tool import sentiment_analysis
from ..Financial.tools.competitor_analysis_tool import competitor_analysis
from ..Financial.tools.risk_assessment_tool import risk_assessment
# from openai import OpenAI
from crewai import LLM
from langchain_openai import ChatOpenAI
import os
os.environ['DEEPSEEK_API_KEY']="sk-ebcb53f7e81a4ee88e1e140a41522f19"
# llm = ChatOpenAI(model="gpt-4-1106-preview")
def create_crew(stock_symbol,openai_api_base_url,openai_api_model_type,openai_api_key):
    # Initialize Ollama LLM
    # llm = Ollama(model="tinyllama")  # Make sure you have the llama2 model installed in Ollama
    print(stock_symbol)
    llm = ChatOpenAI(
        # model="DeepSeek-R1",
        model="deepseek/deepseek-chat",
        # base_url="https://ai.gitee.com/v1",
        base_url="https://api.deepseek.com",
        # api_key="8AORHWT6OWTFKSGEYIPOUPDB7IXZCJCGLR49D5TD",
        api_key="sk-ebcb53f7e81a4ee88e1e140a41522f19"
        # default_headers={"X-Package":"1910"},
    )
    # client = ChatOpenAI(
    #     model=openai_api_model_type,
    #     base_url=openai_api_base_url,
    #     api_key=openai_api_key
    # )

    # llm = LLM(
    #     model=openai_api_model_type,
    #     # base_url="https://ai.gitee.com/v1",
    #     base_url=openai_api_base_url,
    #     # api_key="8AORHWT6OWTFKSGEYIPOUPDB7IXZCJCGLR49D5TD",
    #     api_key=openai_api_key
    # )

    # import litellm
    # from litellm import CustomLLM, completion, get_llm_provider
    #
    # class MyCustomLLM(CustomLLM):
    #     def completion(self, *args, **kwargs) -> litellm.ModelResponse:
    #         return  client.chat.completions.create(*args, **kwargs)
    #
    # my_custom_llm = MyCustomLLM()
    #
    # litellm.custom_provider_map = [  # 👈 KEY STEP - REGISTER HANDLER
    #     {"provider": "my-custom-llm", "custom_handler": my_custom_llm}
    # ]
    # llm=my_custom_llm

    # Define Agents
    researcher = Agent(
        role='Stock Market Researcher',
        goal='Gather and analyze comprehensive data about the stock',
        backstory="You're an experienced stock market researcher with a keen eye for detail and a talent for uncovering hidden trends.最后输出的内容必须是中文内容呈现，不要是英文",
        tools=[yf_tech_analysis, yf_fundamental_analysis, competitor_analysis],
        llm=llm
    )

    analyst = Agent(
        role='Financial Analyst',
        goal='Analyze the gathered data and provide investment insights',
        backstory="You're a seasoned financial analyst known for your accurate predictions and ability to synthesize complex information.最后输出的内容必须是中文内容呈现，不要是英文",
        tools=[yf_tech_analysis, yf_fundamental_analysis, risk_assessment],
        llm=llm
    )

    sentiment_analyst = Agent(
        role='Sentiment Analyst',
        goal='Analyze market sentiment and its potential impact on the stock',
        backstory="You're an expert in behavioral finance and sentiment analysis, capable of gauging market emotions and their effects on stock performance.最后输出的内容必须是中文内容呈现，不要是英文",
        tools=[sentiment_analysis],
        llm=llm
    )

    strategist = Agent(
        role='Investment Strategist',
        goal='Develop a comprehensive investment strategy based on all available data',
        backstory="You're a renowned investment strategist known for creating tailored investment plans that balance risk and reward.最后输出的内容必须是中文内容呈现，不要是英文",
        tools=[],
        llm=llm
    )
    # print('start11')
    description = f"Research {stock_symbol} using advanced technical and fundamental analysis tools. Provide a comprehensive summary of key metrics, including chart patterns, financial ratios, and competitor analysis.最后输出的内容必须是中文内容呈现，不要是英文"
    print(description)
    # Define Tasks
    research_task = Task(
        description=description,
        agent=researcher,
        expected_output=''
    )
    # print('start12')
    description = f"Analyze the market sentiment for {stock_symbol} using news and social media data. Evaluate how current sentiment might affect the stock's performance.最后输出的内容必须是中文内容呈现，不要是英文"
    sentiment_task = Task(
        description=description,
        agent=sentiment_analyst,
        expected_output=''
    )
    description = f"Synthesize the research data and sentiment analysis for {stock_symbol}. Conduct a thorough risk assessment and provide a detailed analysis of the stock's potential."
    analysis_task = Task(
        description=description,
        agent=analyst,
        expected_output=''
    )
    description = f"Based on all the gathered information about {stock_symbol}, develop a comprehensive investment strategy. Consider various scenarios and provide actionable recommendations for different investor profiles.最后输出的内容必须是中文内容呈现，不要是英文"
    strategy_task = Task(
        description=description,
        agent=strategist,
        expected_output=''
    )
    # print('start')
    # Create Crew
    crew = Crew(
        agents=[researcher, sentiment_analyst, analyst, strategist],
        tasks=[research_task, sentiment_task, analysis_task, strategy_task],
        process=Process.sequential
    )
    # print('end')

    return crew

def run_analysis(stock_symbol,openai_api_base_url,openai_api_model_type,openai_api_key):
    crew = create_crew(stock_symbol,openai_api_base_url,openai_api_model_type,openai_api_key)
    result = crew.kickoff()
    return result
