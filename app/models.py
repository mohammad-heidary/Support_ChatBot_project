### app/models.py
from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # 'user' or 'bot'
    content: str

class ChatSession(BaseModel):
    session_id: str
    model_name: Optional[str] = ["llama3-8b-8192", "llama3-70b-8192", "gemma-7b-it"]
    history: List[Message] = []

class UserMessage(BaseModel):
    session_id: str
    content: str
