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
load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

Path("src/data").mkdir(exist_ok=True)


DEFAULT_MODEL = os.getenv("MODEL","qwen3.8-max")

ALLOWED_MODELS = {
    "qwen3.8-flash",
    "deepseek-v4.1-flash"
}