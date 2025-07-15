from fastapi import APIRouter, HTTPException, Depends
from app.models import UserMessage
from app.database import save_message, get_history
from app.agents import get_agent
from app.auth_router import get_current_user
import uuid

chat_router = APIRouter()
sessions = {}

AVAILABLE_MODELS = ["llama3-8b-8192", "llama3-70b-8192", "gemma-7b-it"]

@chat_router.get("/available_models")
def get_available_models():
    return {"models": AVAILABLE_MODELS}

@chat_router.post("/start_chat")
def start_chat(
    model_name: str,
    user: str = Depends(get_current_user)
):
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Model '{model_name}' is not available.")
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "agent": get_agent(model_name),
        "user": user
    }
    return {"session_id": session_id}

@chat_router.post("/send_message")
def send_message(
    message: UserMessage,
    user: str = Depends(get_current_user)
):
    session = sessions.get(message.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["user"] != user:
        raise HTTPException(status_code=403, detail="Unauthorized access to this session")

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
def get_chat_history(
    session_id: str,
    user: str = Depends(get_current_user)
):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["user"] != user:
        raise HTTPException(status_code=403, detail="Unauthorized access to this session")

    return get_history(session_id)
