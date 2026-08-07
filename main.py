import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI(title="EDUMITHRA AI Learning Platform API")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Request schemas
class TopicRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 3

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