from typing import List,Annotated,TypedDict
from langgraph.graph.message import add_messages
from pydantic import BaseMessage
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage],add_messages]