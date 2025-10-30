# backend/app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel
import json
import os
import requests
from dotenv import load_dotenv

from processor import analyze_emails
import json
from typing import Dict, Any
from fastapi import Response

TOKENS_FILE = os.path.join(BASE_DIR if 'BASE_DIR' in globals() else os.path.dirname(os.path.abspath(__file__)), "..", "tokens.json")

def load_tokens() -> Dict[str, Any]:
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_tokens(tokens: Dict[str, Any]):
    try:
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2)
    except Exception:
        pass

# in-memory cache (loaded from file)
TOKENS = load_tokens()


# ✅ Load .env
load_dotenv()

# -------------------------------------------------------
# FastAPI setup
# -------------------------------------------------------
app = FastAPI(title="AI Email Prioritizer - Gmail (OAuth Mode)")

# Allow same-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
templates = Jinja2Templates(directory=FRONTEND_DIR)

# -------------------------------------------------------
# Google OAuth2 Config
# -------------------------------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/oauth2callback")
TOKENS = {}  # memory storage for demo

# -------------------------------------------------------
# Token refresh helper (for multi-account support)
# -------------------------------------------------------
def refresh_access_token_for_user(user_email: str):
    token_obj = TOKENS.get(user_email)
    if not token_obj:
        return False
    refresh_token = token_obj.get("refresh_token")
    if not refresh_token:
        return False

    token_url = "https://oauth2.googleapis.com/token"
    resp = requests.post(token_url, data={
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    data = resp.json()
    if "access_token" in data:
        # update and save
        token_obj.update(data)
        TOKENS[user_email] = token_obj
        save_tokens(TOKENS)
        return True
    return False

# -------------------------------------------------------
# Serve UI (index.html)
# -------------------------------------------------------
@app.get("/")
async def serve_ui(request: Request):
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

# -------------------------------------------------------
# Health check
# -------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# -------------------------------------------------------
# OAuth Login → Redirect to Google
# -------------------------------------------------------
@app.get("/auth/login")
async def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile%20https://www.googleapis.com/auth/gmail.readonly"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(url=google_auth_url)

# -------------------------------------------------------
# OAuth callback → exchange code for access token
# -------------------------------------------------------
from fastapi.responses import RedirectResponse, JSONResponse


@app.get("/oauth2callback")
async def auth_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    res = requests.post(token_url, data=token_data)
    token_json = res.json()

    if "access_token" not in token_json:
        # forward raw response for debugging
        raise HTTPException(status_code=400, detail=token_json)

    # Get user info (email) from Google
    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {token_json['access_token']}"}
    ).json()

    user_email = userinfo.get("email")
    if not user_email:
        raise HTTPException(status_code=400, detail="Failed to fetch user email")

    # Save tokens under this user's email
    TOKENS[user_email] = token_json
    save_tokens(TOKENS)

    # Set a cookie so subsequent requests identify which user is active
    resp = RedirectResponse(url="/")
    # httponly cookie - frontend cannot read this (safer)
    resp.set_cookie(key="user_email", value=user_email, httponly=True, secure=False, samesite="lax")
    return resp

from fastapi.responses import JSONResponse

@app.get("/auth/status")
async def auth_status(request: Request):
    user_email = request.cookies.get("user_email")
    if user_email and user_email in TOKENS:
        # minimal safe info returned to frontend
        return {"logged_in": True, "email": user_email}
    return {"logged_in": False}

@app.get("/auth/logout")
async def auth_logout(request: Request):
    user_email = request.cookies.get("user_email")
    resp = RedirectResponse(url="/")
    if user_email:
        # remove cookie so frontend knows user is logged out
        resp.delete_cookie("user_email")
    return resp


@app.get("/emails")
async def get_emails(request: Request):
    user_email = request.cookies.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated. Please /auth/login first.")
    user_token = TOKENS.get(user_email)
    if not user_token:
        raise HTTPException(status_code=401, detail="No tokens for this user. Please /auth/login again.")

    access_token = user_token.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid token for user. Please /auth/login again.")

    headers = {"Authorization": f"Bearer {access_token}"}
    gmail_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10"

    print("📡 Fetching Gmail message list...")
    msg_list_res = requests.get(gmail_url, headers=headers)
    print("📩 Status code:", msg_list_res.status_code)
    print("📬 Response JSON:", msg_list_res.text[:500])

    if msg_list_res.status_code == 401:
        raise HTTPException(status_code=401, detail="Access token expired or invalid. Please /auth/login again.")

    try:
        msg_list = msg_list_res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid Gmail API response: {e}")

    if "error" in msg_list:
        raise HTTPException(status_code=400, detail=msg_list["error"])

    emails = []
    for m in msg_list.get("messages", []):
        msg = requests.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{m['id']}?format=full",
            headers=headers
        ).json()

        headers_list = msg.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers_list if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers_list if h["name"] == "From"), "")
        date = next((h["value"] for h in headers_list if h["name"] == "Date"), "")
        body = msg.get("snippet", "")

        emails.append({
            "id": m["id"],
            "from": sender,
            "to": "me",
            "subject": subject,
            "body": body,
            "date": date
        })

    analyzed = analyze_emails(emails, hours=24, top_n_summaries=3)
    print(f"✅ Returning {len(analyzed)} analyzed emails")
    return JSONResponse({"count": len(analyzed), "emails": analyzed})
