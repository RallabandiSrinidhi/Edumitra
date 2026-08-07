import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

# --- 1. Database Configuration ---
DATABASE_URL = "sqlite:///./edumithra.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Table Schema
class QuizResultModel(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    topic = Column(String)
    score = Column(Integer)
    total = Column(Integer)

# Create the database file and table automatically
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. FastAPI Setup ---
app = FastAPI(title="EDUMITHRA AI Learning Platform API")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Request Body Schemas
class TopicRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 3

class ScoreSubmit(BaseModel):
    username: str
    topic: str
    score: int
    total: int

# --- 3. Endpoints ---
@app.get("/")
def home():
    return {"message": "Welcome to EDUMITHRA AI Learning Platform"}

@app.post("/explain")
def explain_concept(req: TopicRequest):
    prompt = f"Explain the concept of '{req.topic}' for a {req.difficulty} level student in simple, clear terms with bullet points."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"explanation": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz")
def generate_quiz(req: QuizRequest):
    prompt = f"Generate {req.num_questions} multiple-choice quiz questions on '{req.topic}'. Include 4 options and mark the correct answer for each."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"quiz": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-score")
def submit_score(score_data: ScoreSubmit, db: Session = Depends(get_db)):
    new_result = QuizResultModel(
        username=score_data.username,
        topic=score_data.topic,
        score=score_data.score,
        total=score_data.total
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return {"message": "Score saved successfully!", "data": new_result}

@app.get("/scores")
def get_scores(db: Session = Depends(get_db)):
    return db.query(QuizResultModel).all()