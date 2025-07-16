### app/agents.py
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import TavilySearchResults
from langchain_groq import ChatGroq
from langchain_core.tools import Tool 

import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")
didar_key = os.getenv('DIDAR_API_KEY')

def search_didar_cases(query: str) -> str:
    response = requests.get(
    f"https://api.didar.me/v1/cases?search={query}&apikey={didar_key}")

    if response.status_code != 200:
        return "❗ خطا در دریافت اطلاعات از دیدار."
    cases = response.json()
    if not cases:
        return "موردی پیدا نشد."
    return "\n".join([f"{c['title']} - {c['status']}" for c in cases[:3]])

# You can swap "groq" with any supported model (like "mixtral")
def get_agent(model_name: str):
    llm = ChatGroq(model=model_name, api_key=groq_key)
    
    llm = llm.with_config(system_message="شما یک دستیار ساده پشتیبانی هستید.")

    
    tools = [
        Tool.from_function(
            name="search_didar_cases",
            description="جستجوی درخواست‌های مشتریان در سامانه دیدار",
            func=search_didar_cases ),TavilySearchResults(
    max_results=3,
    include_answer=True,
    include_raw_content=True,
    include_images=False)]

    return create_react_agent(llm, tools=tools)
