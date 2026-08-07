import os
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["AI Modules"])
MODEL_NAME = "llama-3.3-70b-versatile"

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GROQ_API_KEY environment variable is missing or empty."
        )
    return Groq(api_key=api_key)

# --- Schemas ---
class CurriculumRequest(BaseModel):
    career_goal: str
    current_skill_level: str
    weekly_study_hours: int = Field(ge=1, le=80)
    target_duration_weeks: int = Field(ge=1, le=52)

class MilestoneModule(BaseModel):
    phase_title: str
    duration_weeks: int
    topics: List[str]
    practical_project: str

class CurriculumResponse(BaseModel):
    status: str
    career_goal: str
    roadmap: List[MilestoneModule]

class Message(BaseModel):
    role: str
    content: str

class TutorChatRequest(BaseModel):
    user_query: str
    current_topic: Optional[str] = None
    chat_history: List[Message] = []

class TutorChatResponse(BaseModel):
    status: str
    reply: str

# --- Endpoints ---
@router.post("/curriculum/generate", response_model=CurriculumResponse)
async def generate_curriculum(payload: CurriculumRequest):
    client = get_groq_client()
    
    system_prompt = (
        "You are an AI Curriculum Architect. You MUST output strictly valid JSON with 'roadmap' as a LIST of objects. "
        "Strictly follow this structure:\n"
        "{\n"
        '  "roadmap": [\n'
        "    {\n"
        '      "phase_title": "Phase 1: Fundamentals",\n'
        '      "duration_weeks": 2,\n'
        '      "topics": ["Topic A", "Topic B"],\n'
        '      "practical_project": "Build a simple app"\n'
        "    }\n"
        "  ]\n"
        "}"
    )
    
    user_prompt = f"Career Goal: {payload.career_goal}, Skill Level: {payload.current_skill_level}, Weekly Hours: {payload.weekly_study_hours}, Target Weeks: {payload.target_duration_weeks}."
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        raw_data = json.loads(completion.choices[0].message.content)
        roadmap_data = raw_data.get("roadmap", [])
        
        # Convert dictionary to list if LLM returns a single object
        if isinstance(roadmap_data, dict):
            roadmap_data = [roadmap_data]
            
        return CurriculumResponse(
            status="success",
            career_goal=payload.career_goal,
            roadmap=roadmap_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/tutor/chat", response_model=TutorChatResponse)
async def tutor_chat(payload: TutorChatRequest):
    client = get_groq_client()
    system_prompt = f"You are EDUMITHRA AI Tutor. Subject context: {payload.current_topic or 'General Studies'}."
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in payload.chat_history[-6:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": payload.user_query})

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.6
        )
        return TutorChatResponse(
            status="success",
            reply=completion.choices[0].message.content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))