from fastapi import FastAPI, Request, Form, status, HTTPException,File, UploadFile,Query, HTTPException,Depends
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import bcrypt
import uuid
import json
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import os,shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
from typing import Union
import sqlite3
app = FastAPI()

DATA_FILE = "data.json"

DATABASE_URL = "sqlite:///./main.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class SessionToken(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    session_id = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)


Base.metadata.create_all(bind=engine)


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

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: str
    password: str


@app.post("/api/create-account")
def create_account(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=user.username, password=hashed)
    db.add(new_user)
    db.commit()
    return {"status": "success", "username": user.username}


@app.post("/api/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    account = db.query(User).filter(User.username == user.username).first()
    if not account:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(user.password.encode(), account.password.encode()):
        raise HTTPException(status_code=401, detail="Incorrect password")

    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=2)

    session_token = SessionToken(username=user.username, session_id=session_id, expires_at=expires_at)
    db.add(session_token)
    db.commit()

    return {"status": "success", "session_id": session_id, "expires_at": expires_at.isoformat()}


@app.get("/api/check-session")
def check_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionToken).filter(SessionToken.session_id == session_id).first()
    if not session:
        return {"status": "invalid"}
    if session.expires_at < datetime.utcnow():
        return {"status": "expired"}
    return {"status": "valid", "username": session.username}

def clean_split_list(value):
    if isinstance(value, list):
        cleaned = []
        for v in value:
            cleaned.extend([x.strip() for x in v.split(",") if x.strip()])
        return cleaned
    return []

def is_session_valid(session_id: str):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT expires_at FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        expires_at = datetime.fromisoformat(row[0])
        if datetime.utcnow() < expires_at:
            return True
    return False


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
