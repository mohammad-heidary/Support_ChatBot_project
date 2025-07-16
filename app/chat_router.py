from fastapi import APIRouter, HTTPException
from app.models import UserMessage
from app.models import ModelAction
from app.database import save_message, get_history
from app.agents import get_agent
import uuid

chat_router = APIRouter()
sessions = {}

AVAILABLE_MODELS = [
    "llama3-8b-8192",
    "llama3-70b-8192",
    "gemma-7b-it",
    "llama-3.3-70b-versatile",      # new
    "llama-3.1-8b-instant",         # new
    "gemma2-9b-it",                 # new
    "deepseek-r1-distill-llama-70b"  # if you want to test
]

@chat_router.post("/model_action")
def model_action(body: ModelAction):
    action = body.action
    model_name = body.model_name
    if action == "list":
        return {
            "models": AVAILABLE_MODELS,
            "description": "Select one of the supported LLMs for your session."
        }

    elif action == "start":
        if not model_name:
            raise HTTPException(status_code=400, detail="Model name is required for starting a chat.")
        if model_name not in AVAILABLE_MODELS:
            raise HTTPException(status_code=400, detail=f"Model '{model_name}' is not available.")
        
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "agent": get_agent(model_name)
        }
        return {"session_id": session_id}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'list' or 'start'.")

@chat_router.post("/send_message")
def send_message(message: UserMessage):
    session = sessions.get(message.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = session["agent"]
    save_message(message.session_id, "user", message.content)

    response = agent.invoke({"messages": [{"role": "user", "content": message.content}]})
    print("RESPONSE:", response)

    try:
        ai_message = response["messages"][-1]
        output = ai_message.content
    except Exception as e:
        output = f"❗ خطا در پردازش پاسخ: {str(e)}"

    save_message(message.session_id, "bot", output)
    return {"response": output}

@chat_router.get("/get_history/{session_id}")
def get_chat_history(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return get_history(session_id)
