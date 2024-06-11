from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    mobile_no = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Discussion(Base):
    __tablename__ = "discussions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    view_count = Column(Integer, default=0)

    user = relationship("User")

class Hashtag(Base):
    __tablename__ = "hashtags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class DiscussionHashtag(Base):
    __tablename__ = "discussion_hashtags"
    discussion_id = Column(Integer, ForeignKey("discussions.id"), primary_key=True)
    hashtag_id = Column(Integer, ForeignKey("hashtags.id"), primary_key=True)

Base.metadata.create_all(bind=engine)

class DiscussionCreate(BaseModel):
    user_id: int
    text: str
    image_url: Optional[str] = None
    hashtags: Optional[List[str]] = []

class DiscussionUpdate(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None
    hashtags: Optional[List[str]] = None

@app.post("/discussions/", response_model=DiscussionCreate)
def create_discussion(discussion: DiscussionCreate):
    db = SessionLocal()
    db_discussion = Discussion(
        user_id=discussion.user_id,
        text=discussion.text,
        image_url=discussion.image_url,
    )
    db.add(db_discussion)
    db.commit()
    db.refresh(db_discussion)

    for hashtag in discussion.hashtags:
        db_hashtag = db.query(Hashtag).filter(Hashtag.name == hashtag).first()
        if not db_hashtag:
            db_hashtag = Hashtag(name=hashtag)
            db.add(db_hashtag)
            db.commit()
            db.refresh(db_hashtag)
        db_discussion_hashtag = DiscussionHashtag(discussion_id=db_discussion.id, hashtag_id=db_hashtag.id)
        db.add(db_discussion_hashtag)
        db.commit()

    db.close()
    return db_discussion

@app.put("/discussions/{discussion_id}", response_model=DiscussionCreate)
def update_discussion(discussion_id: int, discussion: DiscussionUpdate):
    db = SessionLocal()
    db_discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not db_discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    if discussion.text:
        db_discussion.text = discussion.text
    if discussion.image_url:
        db_discussion.image_url = discussion.image_url
    
    db.commit()
    db.refresh(db_discussion)
    
    if discussion.hashtags:
        db.query(DiscussionHashtag).filter(DiscussionHashtag.discussion_id == discussion_id).delete()
        for hashtag in discussion.hashtags:
            db_hashtag = db.query(Hashtag).filter(Hashtag.name == hashtag).first()
            if not db_hashtag:
                db_hashtag = Hashtag(name=hashtag)
                db.add(db_hashtag)
                db.commit()
                db.refresh(db_hashtag)
            db_discussion_hashtag = DiscussionHashtag(discussion_id=db_discussion.id, hashtag_id=db_hashtag.id)
            db.add(db_discussion_hashtag)
            db.commit()

    db.close()
    return db_discussion

@app.delete("/discussions/{discussion_id}", response_model=DiscussionCreate)
def delete_discussion(discussion_id: int):
    db = SessionLocal()
    db_discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not db_discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    db.query(DiscussionHashtag).filter(DiscussionHashtag.discussion_id == discussion_id).delete()
    db.delete(db_discussion)
    db.commit()
    db.close()
    return db_discussion

@app.get("/discussions/", response_model=List[DiscussionCreate])
def list_discussions():
    db = SessionLocal()
    discussions = db.query(Discussion).all()
    db.close()
    return discussions

@app.get("/discussions/search", response_model=List[DiscussionCreate])
def search_discussions(tag: Optional[str] = None, text: Optional[str] = None):
    db = SessionLocal()
    if tag:
        discussions = db.query(Discussion).join(DiscussionHashtag).join(Hashtag).filter(Hashtag.name == tag).all()
    elif text:
        discussions = db.query(Discussion).filter(Discussion.text.ilike(f"%{text}%")).all()
    else:
        discussions = []
    db.close()
    return discussions
