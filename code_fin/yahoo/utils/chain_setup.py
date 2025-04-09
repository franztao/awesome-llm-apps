from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents.format_scratchpad import format_to_openai_functions

def create_chain(tools, openai_api_base_url,openai_api_model_type,openai_api_key):
    functions = [format_tool_to_openai_function(f) for f in tools]
    
    # TODO: use better model with larger context window
    # model = ChatOpenAI(model="DeepSeek-R1",base_url="https://ai.gitee.com/v1",api_key="XWKOBFEFOYJYDXAIONEQBBHLX5TTEEUIN70JTZA6", temperature=0).bind(functions=functions)
    model = ChatOpenAI(
        model=openai_api_model_type,
        base_url=openai_api_base_url,
        api_key=openai_api_key
    , temperature=0).bind(functions=functions)
    # client = OpenAI(
    #     base_url="https://ai.gitee.com/v1",
    #     # base_url="https://api.deepseek.com",
    #     api_key="8AORHWT6OWTFKSGEYIPOUPDB7IXZCJCGLR49D5TD",
    #     # api_key="sk-ebcb53f7e81a4ee88e1e140a41522f19"
    #     # default_headers={"X-Package":"1910"},
    # )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a highly knowledgeable financial assistant. You provide accurate and detailed financial data, analysis, and recommendations. Use the appropriate tools to fetch real-time data when needed.最后输出的内容必须是中文内容呈现，不要是英文"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "User is asking: {input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        # ("system", "Based on the available information and tools, generate a concise and accurate response. If additional data is needed, use the corresponding tool."),
    ])

    chain = prompt | model | OpenAIFunctionsAgentOutputParser()

    agent_chain = RunnablePassthrough.assign(
        agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
    ) | chain

    return agent_chain
