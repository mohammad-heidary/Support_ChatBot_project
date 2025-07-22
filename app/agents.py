### app/agents.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.tools import Tool 

import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base_url = os.getenv("OPENAI_API_BASE") 

tavily_key = os.getenv("TAVILY_API_KEY")
didar_key = os.getenv('DIDAR_API_KEY')


def search_didar_cases(query: str) -> str:
    response = requests.get(
        f"https://app.didar.me/api/contact/save?apikey={didar_key}")
    if response.status_code != 200:
        return "❗ Error retrieving information from the meeting."
    cases = response.json()
    if not cases:
        return "No items found."
    return "\n".join([f"{c['title']} - {c['status']}" for c in cases[:3]])

search_didar_tool = Tool.from_function(
    name="search_didar_cases",
    description="Search for customer requests in the Didar system. The input must be a search string.",
    func=search_didar_cases
)


def get_agent(model_name: str):
    llm = ChatOpenAI(
        model_name=model_name,
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url,
        model_kwargs={
            "headers": {
                "HTTP-Referer": "https://support-bot-didar.darkube.app",   # Enter your app domain
                "X-Title": "SupportBot"
            }
        }
    )

    llm = llm.with_config(system_message="""
You are a helpful assistant. Always respond in English and use tools when needed.
    """)

    tools = [search_didar_tool, TavilySearchResults(max_results=3)]

    return create_react_agent(llm, tools=tools)
    tools = [search_didar_tool, TavilySearchResults(max_results=3)]

    return create_react_agent(llm, tools=tools)
