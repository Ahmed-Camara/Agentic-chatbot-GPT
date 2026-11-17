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
from langchain_anthropic import ChatAnthropic
from prompt import SYSTEM_PROMPT
load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

Path("src/data").mkdir(exist_ok=True)


DEFAULT_MODEL = os.getenv("MODEL","claude-opus-4-8")
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

ALLOWED_MODELS = {
    "claude-sonnet-5",
    "claude-opus-5-5",
    "claude-fable-5-1"
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
    
    llm = ChatAnthropic(model=selected_model,api_key=API_KEY,
                     base_url=BASE_URL,temperature=0.3,streaming=True)
    
    llm_with_tools = llm.bind_tools(tools)
    
    def chat_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        
        response = llm_with_tools.invoke(messages)
        
        return {
            "messages":[response]
        }
    
    tool_node = ToolNode(tools)
    
    graph = StateGraph(MessagesState)
    
    graph.add_node("chat_node",chat_node)
    graph.add_node("tools",tool_node)
    
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge("tools","chat_node")
    
    conn = sqlite3.connect("data/langgraph_checkpoints.sqlite",
                           check_same_thread=False)
    
    checkpointer = SqliteSaver(conn)
    return graph.compile(checkpointer=checkpointer)
    
    