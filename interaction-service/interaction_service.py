
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine("postgresql://user:password@db/mydatabase")
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class CommentCreate(BaseModel):
    discussion_id: int
    user_id: int
    text: str

@app.post("/comments/")
def create_comment(comment: CommentCreate):
    db = SessionLocal()
    db_comment = Comment(discussion_id=comment.discussion_id, user_id=comment.user_id, text=comment.text)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    db.close()
    return db_comment

class LikeCreate(BaseModel):
    discussion_id: int
    user_id: int

@app.post("/likes/")
def create_like(like: LikeCreate):
    db = SessionLocal()
    db_like = Like(discussion_id=like.discussion_id, user_id=like.user_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    db.close()
    return db_like
