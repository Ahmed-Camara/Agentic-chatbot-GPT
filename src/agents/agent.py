from dotenv import load_dotenv
import os
import sqlite3
import certifi
from pathlib import Path
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START,MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from src.tools.tools import get_current_weather
from prompt import SYSTEM_PROMPT
load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

Path("src/data").mkdir(exist_ok=True)


DEFAULT_MODEL = os.getenv("MODEL","qwen3.8-max")
BASE_URL = os.getenv("BASE_URL")

ALLOWED_MODELS = {
    "qwen3.8-flash",
    "deepseek-v4.1-flash"
}

tools = []
def normalize_model_name(model_name: str | None):
    
    if not model_name:
        return DEFAULT_MODEL
    model_name = model_name.strip()
    
    if model_name not in ALLOWED_MODELS:
        return DEFAULT_MODEL
    
    return model_name

def build_agent(model_name: str):
    """
        Build one langgraph agent for a selected model.
    """
    
    selected_model = normalize_model_name(model_name)
    
    llm = ChatOpenAI(model=selected_model,
                     base_url=BASE_URL,temperature=0.3,streaming=True)
    
    llm_with_tools = llm.bind_tools(tools)
    
    def chat_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
    