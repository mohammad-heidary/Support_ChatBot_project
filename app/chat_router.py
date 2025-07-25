from fastapi import APIRouter, HTTPException
from app.models import UserMessage
from app.database import save_message, get_history
from app.agents import get_agent
import traceback




chat_router = APIRouter()
sessions = {}

DEFAULT_MODEL = "mistralai/mistral-7b-instruct"

WELCOME_MESSAGE = "hi! how can i help you? 😊"

@chat_router.post("/send_message")
def send_message(message: UserMessage):
    session_id = message.session_id
    content = message.content

    
    # If the session does not exist, create it
    if session_id not in sessions:
        sessions[session_id] = {"agent": get_agent(DEFAULT_MODEL)}

    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=403, detail="Invalid or expired session_id.")

    # Count the number of previous messages from the user
    history = get_history(session_id)
    user_message_count = sum(1 for msg in history if msg["role"] == "user")

    if user_message_count >= 20:
        return {
            "response": "⚠️ You can only send 20 messages in this session. Please start a new session."}

    # Continue the usual process
    agent = session["agent"]
    save_message(session_id, "user", content)

    response = agent.invoke({"messages": [{"role": "user", "content": content}]})

  #  print (f"⚠️ Raw response: {response}")
    try:
        ai_message = response["messages"][-1]
        output = ai_message.content
    except Exception as e:
            traceback.print_exc()
            output = f"❗ Error processing response: {str(e)}"
    
    return {"response": output}


@chat_router.get("/get_history/{session_id}")
def get_chat_history(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return get_history(session_id)
