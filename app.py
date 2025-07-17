from fastapi import FastAPI, Request, Form, status, HTTPException,File, UploadFile,Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import os,shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
from typing import Union


app = FastAPI()

# Set up templates folder
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "data.json"

ACCOUNTS_FILE = "accounts.json"

# Create the JSON file if it doesn't exist
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump({"users": []}, f)

class UserCreate(BaseModel):
    username:str
    password:str

def load_accounts():
    with open(ACCOUNTS_FILE,'r') as f:
        return json.load(f)


def save_accounts(data):
    with open(ACCOUNTS_FILE,'w') as f:
        json.dump(data,f,indent=2)



class VideoEntry(BaseModel):
    title: str
    description: str
    thumbnail: str
    videourl: List[str]  # ✅ now expecting a list always
    tag: List[str]
    category: List[str]

class UploadData(BaseModel):
    uploader: str
    session_id: str
    videos: List[VideoEntry]

# -------------------
# File helpers
# -------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"data": {"data": []}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"data": {"data": []}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Utils
def load_json(file): return json.load(open(file))
def save_json(file, data): json.dump(data, open(file, "w"), indent=2)

# ROUTES
@app.get("/", response_class=HTMLResponse)
def show_create_account(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# -------------------
# POST API to add profile
# -------------------

SESSION_FILE = "sessions.json"

def load_sessions():
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def is_session_valid(session_id: str):
    sessions = load_sessions()
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            return datetime.utcnow() < datetime.fromisoformat(session["expires_at"])
    return False

@app.get("/api/session-info")
def session_info(session_id: str):
    sessions = load_json("sessions.json")
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
                return {"status": "success", "username": session["username"]}
            break
    return {"status": "error", "detail": "Session invalid or expired"}


@app.post("/api/add/sundarikanya", status_code=201)
def add_sundari_entry(data: UploadData):
    # ✅ Validate session
    if not is_session_valid(data.session_id):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    store = load_data()
    existing = store.get("data", {}).get("data", [])

    added_count = 0

    for video in data.videos:
        # ✅ Create one entry with multiple video URLs
        new_id = f"{len(existing) + 1:03d}"
        new_entry = {
            "id": new_id,
            "uploader": data.uploader,
            "title": video.title,
            "description": video.description,
            "thumbnail": video.thumbnail,
            "videourl": video.videourl,  # ✅ entire list
            "tag": video.tag,
            "category": video.category
        }
        existing.append(new_entry)
        added_count += 1

    store["data"]["data"] = existing
    save_data(store)

    return {"status": "success", "added": added_count}





@app.get("/api/get/sundarikanya")
def get_video_by_id(id: Optional[str] = Query(None)):
    data = load_data()["data"]["data"]

    # If no id is passed, return all videos
    if id is None:
        return data

    # Format ID to 3 digits (e.g., "2" → "002")
    formatted_id = id.zfill(3)

    # Find the video with matching ID
    result = next((item for item in data if item["id"] == formatted_id), None)

    if not result:
        raise HTTPException(status_code=404, detail=f"Video with ID {formatted_id} not found.")

    return result

# Utility: Convert ["Pakistani,Teen,,Model"] → ["Pakistani", "Teen", "Model"]
def clean_split_list(value):
    if isinstance(value, list):
        cleaned = []
        for v in value:
            cleaned.extend([x.strip() for x in v.split(",") if x.strip()])
        return cleaned
    return []

@app.get("/api/get/sundarikanya1")
def get_sundari_entries(
    category: Optional[str] = None,
    tag: Optional[str] = None
):
    store = load_data()  # Load your JSON DB or file
    all_entries = store.get("data", {}).get("data", [])

    filtered_entries = []

    for entry in all_entries:
        cat_list = clean_split_list(entry.get("category", []))
        tag_list = clean_split_list(entry.get("tag", []))

        match_category = True
        match_tag = True

        if category:
            match_category = any(c.lower() == category.lower() for c in cat_list)

        if tag:
            match_tag = any(t.lower() == tag.lower() for t in tag_list)

        if match_category and match_tag:
            filtered_entries.append(entry)

    return {
        "status": "success",
        "filter": {"category": category, "tag": tag},
        "count": len(filtered_entries),
        "data": filtered_entries
    }


@app.get("/api/get/search")
def search_sundari_entries(
    query: str = Query(..., description="Search by keyword in title, description, tag, or category")
):
    data_store = load_data()
    all_entries = data_store.get("data", {}).get("data", [])

    query_lower = query.lower()
    results = []

    for entry in all_entries:
        title_match = query_lower in entry.get("title", "").lower()
        description_match = query_lower in entry.get("description", "").lower()

        tag_match = any(query_lower in tag.lower() for tag in entry.get("tag", []))
        category_match = any(query_lower in cat.lower() for cat in entry.get("category", []))

        if title_match or description_match or tag_match or category_match:
            results.append(entry)

    return {
        "status": "success",
        "query": query,
        "count": len(results),
        "data": results
    }


@app.get("/api/get/bestcategory")
def get_best_category():
    data_store = load_data()
    all_entries = data_store.get("data", {}).get("data", [])

    category_counter = {}

    for entry in all_entries:
        categories = entry.get("category", [])
        for cat in categories:
            cat_clean = cat.strip().lower()
            if cat_clean:
                category_counter[cat_clean] = category_counter.get(cat_clean, 0) + 1

    # Sort categories by count descending
    sorted_categories = sorted(category_counter.items(), key=lambda x: x[1], reverse=True)

    best_categories = [{"category": cat, "count": count} for cat, count in sorted_categories]

    return {
        "status": "success",
        "total_categories": len(best_categories),
        "best_categories": best_categories
    }



@app.post("/api/create-account")
def create_account(user: UserCreate):
    data = load_json(ACCOUNTS_FILE)
    if any(u["username"] == user.username for u in data["users"]):
        return {"status": "error", "detail": "Username already exists"}
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    data["users"].append({"username": user.username, "password": hashed})
    save_json(ACCOUNTS_FILE, data)
    return {"status": "success", "username": user.username}


from datetime import datetime, timedelta
import uuid

SESSION_FILE = "sessions.json"

# Load/Save session functions
def load_sessions():
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            json.dump({"sessions": []}, f)
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.post("/api/login")
def login(user: UserCreate):
    accounts = load_accounts()
    for account in accounts["users"]:
        if account["username"] == user.username:
            if bcrypt.checkpw(user.password.encode("utf-8"), account["password"].encode("utf-8")):
                # Generate session
                session_id = str(uuid.uuid4())
                expiry_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()

                # Store session
                sessions = load_sessions()
                sessions["sessions"].append({
                    "username": user.username,
                    "session_id": session_id,
                    "expires_at": expiry_time
                })
                save_sessions(sessions)

                return {
                    "status": "success",
                    "message": "Login successful",
                    "session_id": session_id,
                    "expires_at": expiry_time
                }

            else:
                raise HTTPException(status_code=401, detail="Incorrect password")

    raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/check-session")
def check_session(session_id: str):
    sessions = load_sessions()
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
                return {"status": "valid", "username": session["username"]}
            else:
                return {"status": "expired"}
    return {"status": "invalid"}
