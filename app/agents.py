### app/agents.py
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

# You can swap "groq" with any supported model (like "mixtral")
def get_agent(model_name: str):
    llm = ChatGroq(model=model_name, api_key = groq_key)
    llm = llm.with_config(system_message="""
شما یک بات پشتیبانی هوشمند هستید که به سوالات مشتریان درباره خدمات شرکت، شرایط ثبت‌نام، قیمت‌ها و زمان پشتیبانی پاسخ می‌دهید.
""")
    tools = []
    return create_react_agent(llm, tools=tools)
