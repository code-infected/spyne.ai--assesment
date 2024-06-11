from fastapi import FastAPI 
from pydantic import BaseModel 
from sqlalchemy import create_engine, Column, Integer, String, DateTime 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
engine = create_engine("postgresql://user:password@db/mydatabase") 
Base = declarative_base() 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
class User(Base): 
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, index=True) 
    mobile_no = Column(String, unique=True, index=True) 
    email = Column(String, unique=True, index=True) 
    password_hash = Column(String) 
Base.metadata.create_all(bind=engine) 
app = FastAPI() 
class UserCreate(BaseModel): 
    name: str 
    mobile_no: str 
    email: str 
    password: str 
@app.post("/users/") 
def create_user(user: UserCreate): 
    db = SessionLocal() 
    db_user = User(name=user.name, mobile_no=user.mobile_no, email=user.email, password_hash=user.password) 
    db.add(db_user) 
    db.commit() 
    db.refresh(db_user) 
    db.close() 
    return db_user 
