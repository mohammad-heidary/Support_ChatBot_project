from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.users_db import create_user, verify_user
from app.auth_utils import create_access_token, decode_token

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@auth_router.post("/signup")
def signup(form_data: OAuth2PasswordRequestForm = Depends()):
    success = create_user(form_data.username, form_data.password)
    if not success:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"msg": "User created"}

@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not verify_user(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": form_data.username})
    
    # Create a default session for this user
    session_id = str(uuid.uuid4())
    from app.agents import get_agent
    from app.main import sessions, DEFAULT_MODEL, WELCOME_MESSAGE
    sessions[session_id] = {"agent": get_agent(DEFAULT_MODEL)}
    
    from app.database import save_message
    save_message(session_id, "bot", WELCOME_MESSAGE)

    return {
        "access_token": token,
        "token_type": "bearer",
        "session_id": session_id,
        "welcome": WELCOME_MESSAGE
    }


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
