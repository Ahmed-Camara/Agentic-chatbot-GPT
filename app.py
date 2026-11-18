import dotenv
import certifi
import os
import json
import uuid
import uvicorn
from fastapi import FastAPI, Request,UploadFile,File, Form
from fastapi.responses import StreamingResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage,AIMessageChunk
from src.agents.agent import get_agent
from src.db.database import init_db,save_chat_message,get_chat_history,create_or_update_conversation,list_conversations
from src.rag.rag import add_document_to_rag
from src.tools.tools import set_current_thread_id
from pathlib import Path
from src.utils.utils import should_stream_chunk,sse_data,extract_text_from_chunk

from src.utils.variables import UPLOAD_PATH,CHROMA_DB_PATH
app = FastAPI()
Path(UPLOAD_PATH).mkdir(parents=True,exist_ok=True)
Path(CHROMA_DB_PATH).mkdir(parents=True,exist_ok=True)
templates = Jinja2Templates(directory="templates")

init_db()

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )
    
@app.get("/conversations")
async def conversations():
    items = list_conversations()
    
    return {
        "conversations":[
            {
                "thread_id":item.thread_id,
                "title":item.title,
                "created_at":item.created_at.isoformat(),
                "updated_at":item.updated_at.isoformat()
                
            }
            for item in items
        ]
    }
    
@app.get("/history/{thread_id}")
async def history(thread_id: str):
    messages = get_chat_history(thread_id)
    
    return {
        "messages":[
            {
                "role":msg.role,
                "content": msg.content
            } for msg in messages
        ]
    }
@app.post("/upload")
async def upload(file: UploadFile = File(...), thread_id: str = Form(...)):
    
    try:
        allowed_extensions = [".pdf",".docx",".txt",".md",".py",".csv"]
        
        filename = file.filename or "uploaded_file"
        
        suffix = Path(filename).suffix.lower()
        
        if suffix not in allowed_extensions:
            return JSONResponse({
                "success":False,
                "message":"Unsupported file type. Upload PDF, DOCX,TXT, MD, PY, or CSV."
            })
        file_id = str(uuid.uuid4())
        safe_filename = filename.replace(" ","_")
        file_path = f"{UPLOAD_PATH}/{file_id}_{safe_filename}"
        
        with open(file_path,"wb") as f:
            f.write(await file.read())
        
        create_or_update_conversation(thread_id,"uploaded document")
        
        result = add_document_to_rag(file_path=file_path, thread_id=thread_id)
        
        return JSONResponse({
            "success":True,
            "message":f"Uploaded {result['filename']} and created {result['chunks']} chunks."
        })
    except Exception as e:
        return JSONResponse({
                    "success":False,
                    "message":str(e)
                })
        
        
@app.post("/chat/stream")
async def chat_stream(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({
            "error":"Invalid JSON body."
        },status_code=400)
        
    
    user_message = data.get("message","")
    thread_id = data.get("thread_id","default")
    selected_model = data.get("model","qwen3.8-flash")
    
    if not user_message.strip():
        return JSONResponse({
            "error":"Message is required."
        },status_code=400)
        
    agent = get_agent(selected_model)
    
    create_or_update_conversation(thread_id,user_message)
    save_chat_message(thread_id,"user",user_message)
    set_current_thread_id(thread_id)
    config = {
        "configurable":{
            "thread_id":thread_id
        }
    }
    
    def event_generator():
        from openai import APIError
        final_answer = ""
        
        try:
            inputs = {
                "messages":[
                    HumanMessage(content=user_message)
                ]
            }
            
            for chunk, metadata in agent.stream(
                inputs,
                config=config,
                stream_mode="messages"
            ):
                if not should_stream_chunk(chunk,metadata):
                    continue
                
                token = extract_text_from_chunk(chunk)
                
                if token:
                    final_answer += token
                    yield sse_data({"token":token})
                    
            if final_answer.strip():
                save_chat_message(thread_id,"assistant",final_answer)
            yield sse_data({"done":True})
            
        except APIError as e:
            if "inappropriate content" in str(e):
                yield sse_data({"error": "La réponse a été bloquée par le filtre de contenu du modèle. "
                                         "Reformulez la question ou essayez un autre modèle."})
            else:
                yield sse_data({"error": str(e)})
            yield sse_data({"done": True})
        except Exception as e:
            import traceback
            traceback.print_exc() 
            yield sse_data({"error":str(e)})
            yield sse_data({"done":True})
        
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={}
    )
    
if __name__=="__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=9009,
        reload=True
    )



"""

from langchain_core.messages import HumanMessage
agent = get_agent("claude-opus-4-8")

config = {
    "configurable":{
        "thread_id":"test-id"
    }
}
res = agent.invoke({
    "messages":[HumanMessage(content="What is my name ?")]
},config=config)

print(res)
"""