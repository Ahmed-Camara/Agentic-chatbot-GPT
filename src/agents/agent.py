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
from src.tools.tools import Tools
from langchain_anthropic import ChatAnthropic
from src.agents.prompt import SYSTEM_PROMPT
load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

Path("src/data").mkdir(exist_ok=True)


DEFAULT_MODEL = os.getenv("MODEL","qwen3.8-flash")
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

ALLOWED_MODELS = {
    "qwen3.8-max",
    "qwen3.8-flash",
    "deepseek-v4.1-flash"
}



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
    
    llm = ChatOpenAI(model=selected_model,api_key=API_KEY,
                     base_url=BASE_URL,temperature=0.3,streaming=True)
    
    llm_with_tools = llm.bind_tools(Tools)
    
    def chat_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        
        response = llm_with_tools.invoke(messages)
        
        return {
            "messages":[response]
        }
    
    tool_node = ToolNode(Tools)
    
    graph = StateGraph(MessagesState)
    
    graph.add_node("chat_node",chat_node)
    graph.add_node("tools",tool_node)
    
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge("tools","chat_node")
    
    conn = sqlite3.connect("src/data/langgraph_checkpoints.sqlite",
                           check_same_thread=False)
    
    checkpointer = SqliteSaver(conn)
    return graph.compile(checkpointer=checkpointer)
    
    
    
_AGENT_CACHE = {}

def get_agent(model_name: str | None = None):
    """
        Return cached LangGraph agent for selected model.
        If not created yet, create it once and reuse it.
    """
    
    selected_model = normalize_model_name(model_name)
    
    if selected_model not in _AGENT_CACHE:
        _AGENT_CACHE[selected_model] = build_agent(selected_model)
        
    return _AGENT_CACHE[selected_model]
    