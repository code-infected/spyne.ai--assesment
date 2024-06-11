from fastapi import FastAPI, HTTPException, Query
from typing import List
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Dummy data storage (replace this with actual database operations)
discussions_db = []

class Discussion(BaseModel):
    text: str
    image: str = None
    hashtags: List[str]
    created_at: datetime = datetime.now()
    view_count: int = 0

@app.post("/discussions/", response_model=Discussion)
def create_discussion(discussion: Discussion):
    discussions_db.append(discussion)
    return discussion

@app.get("/discussions/", response_model=List[Discussion])
def list_discussions_based_on_tags(tags: List[str] = Query(...)):
    filtered_discussions = []
    for discussion in discussions_db:
        if any(tag in discussion.hashtags for tag in tags):
            filtered_discussions.append(discussion)
    return filtered_discussions

@app.get("/discussions/search", response_model=List[Discussion])
def search_discussions(text: str = Query(None), tags: List[str] = Query(None)):
    filtered_discussions = []
    for discussion in discussions_db:
        if text and text.lower() in discussion.text.lower():
            filtered_discussions.append(discussion)
        if tags and any(tag in discussion.hashtags for tag in tags):
            filtered_discussions.append(discussion)
    return filtered_discussions
