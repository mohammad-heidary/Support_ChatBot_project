from fastapi import APIRouter, HTTPException
from app.models import UserMessage
from app.database import save_message, get_history
from app.agents import get_agent
import uuid

chat_router = APIRouter()
sessions = {}

#DEFAULT_MODEL = "llama-3.1-8b-instant"
DEFAULT_MODEL = "llama3-8b-8192"

WELCOME_MESSAGE = "hi! how can i help you? 😊"

@chat_router.post("/send_message")
def send_message(message: UserMessage):
    session_id = message.session_id
    session = sessions.get(session_id)

    if not session:
    session_id = message.session_id if message.session_id and message.session_id != "string" else str(uuid.uuid4())
    sessions[session_id] = {
        "agent": get_agent(DEFAULT_MODEL)
    }
    session = sessions[session_id]

    return {
        "session_id": session_id,
        "new_session": True
    }



    # Count the number of previous messages from the user
    history = get_history(session_id)
    user_message_count = sum(1 for msg in history if msg["role"] == "user")

    if user_message_count >= 5:
        return {
            "response": "⚠️ You can only send 5 messages in this session. Please start a new session."
        }

    # Continue the usual process
    agent = session["agent"]
    save_message(session_id, "user", message.content)

    response = agent.invoke({"messages": [{"role": "user", "content": message.content}]})

    try:
        ai_message = response["messages"][-1]
        output = ai_message.content
    except Exception as e:
        output = f"❗ Error processing response: {str(e)}"

    save_message(session_id, "bot", output)
    return {"response": output}


@chat_router.get("/get_history/{session_id}")
def get_chat_history(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return get_history(session_id)
