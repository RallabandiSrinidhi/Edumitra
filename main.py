import os
from fastapi import FastAPI
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="EDUMITHRA API")

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/")
def home():
    return {"message": "Welcome to EDUMITHRA AI Learning Platform"}

@app.post("/generate")
def generate_response(prompt: str):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return {"response": completion.choices[0].message.content}