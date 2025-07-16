from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

BOT_USERNAME = "widget-bot"
BOT_PASSWORD = "123456"

# Endpoint for serving HTML chat widget
@router.get("/chat-widget", response_class=HTMLResponse)
def serve_widget(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Register the bot user if not exists (you can place this in app.main)
def ensure_bot_user():
    try:
        requests.post("http://127.0.0.1:8000/auth/signup", data={
            "username": BOT_USERNAME,
            "password": BOT_PASSWORD
        })
    except:
        pass  # Already exists

# Get access token to use in widget requests
def get_bot_token():
    ensure_bot_user()
    response = requests.post("http://127.0.0.1:8000/auth/login", data={
        "username": BOT_USERNAME,
        "password": BOT_PASSWORD
    })
    return response.json().get("access_token")
