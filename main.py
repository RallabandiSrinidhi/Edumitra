import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt

load_dotenv()

# --- Security Configuration ---
SECRET_KEY = "edumithra_super_secret_jwt_key_change_me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Database Setup (SQLite & SQLAlchemy ORM) ---
DATABASE_URL = "sqlite:///./edumithra.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models (Epic 2 Database Integration) ---
class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class CareerPathModel(Base):
    __tablename__ = "career_paths"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    career_goal = Column(String)
    skill_level = Column(String)

class CurriculumModel(Base):
    __tablename__ = "curriculums"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    career_goal = Column(String)
    roadmap = Column(String)

class QuizResultModel(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    topic = Column(String)
    score = Column(Integer)
    total = Column(Integer)

class ProgressTrackingModel(Base):
    __tablename__ = "progress_tracking"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    topic_completed = Column(String)
    streak_count = Column(Integer, default=1)
    completion_percentage = Column(Float, default=0.0)

class AchievementModel(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    title = Column(String)
    description = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper Functions ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- FastAPI Initialization ---
app = FastAPI(title="EDUMITHRA AI Learning Platform - Epic 2 Core")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Pydantic Request Schemas ---
class UserRegister(BaseModel):
    username: str
    password: str

class CurriculumRequest(BaseModel):
    career_goal: str
    skill_level: str = "beginner"
    timeline_weeks: int = 4

class ProgressUpdate(BaseModel):
    topic_completed: str
    streak_count: int
    completion_percentage: float

# --- MODULE 1: USER MANAGEMENT SYSTEM ---
@app.post("/register", tags=["1. User Management"])
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = UserModel(username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully!"}

@app.post("/login", tags=["1. User Management"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", tags=["1. User Management"])
def profile(current_user: UserModel = Depends(get_current_user)):
    return {"username": current_user.username, "status": "Active Session"}

# --- MODULE 2: CURRICULUM GENERATION ---
@app.post("/generate-curriculum", tags=["2. Curriculum Generation"])
def generate_curriculum(
    req: CurriculumRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prompt = f"""
    Act as an expert career mentor. Generate a structured {req.timeline_weeks}-week learning roadmap for a student aiming to become a '{req.career_goal}'.
    Current Skill Level: {req.skill_level}.
    Structure the response into:
    - Phase 1: Core Fundamentals
    - Phase 2: Intermediate Concepts & Tools
    - Phase 3: Practical Projects & Portfolio
    - Recommended Daily Habits & Educational Resources
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        roadmap_content = completion.choices[0].message.content
        
        # Save generated roadmap to database
        new_curr = CurriculumModel(
            username=current_user.username,
            career_goal=req.career_goal,
            roadmap=roadmap_content
        )
        db.add(new_curr)
        db.commit()
        
        return {"career_goal": req.career_goal, "roadmap": roadmap_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- MODULE 3: PROGRESS TRACKING SYSTEM ---
@app.post("/progress/update", tags=["3. Progress Tracking"])
def update_progress(
    p_data: ProgressUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_progress = ProgressTrackingModel(
        username=current_user.username,
        topic_completed=p_data.topic_completed,
        streak_count=p_data.streak_count,
        completion_percentage=p_data.completion_percentage
    )
    db.add(new_progress)
    db.commit()
    return {"message": "Progress recorded successfully!", "data": p_data}

@app.get("/progress/dashboard", tags=["3. Progress Tracking"])
def get_user_progress(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(ProgressTrackingModel).filter(ProgressTrackingModel.username == current_user.username).all()
    quizzes = db.query(QuizResultModel).filter(QuizResultModel.username == current_user.username).all()
    return {
        "username": current_user.username,
        "completed_topics": [r.topic_completed for r in records],
        "quiz_history": quizzes
    }