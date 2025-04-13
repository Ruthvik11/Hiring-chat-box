from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("openai_secrete_key"))


app = FastAPI(title="Hiring Assistant AI")

class TechStackRequest(BaseModel):
    name: str
    email: str
    number: int
    position: str
    experience: str
    tech_stack: str

class Questions(BaseModel):
    questions : str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hiring Assistant API"}

@app.post("/generate-questions", response_model=Questions)
def generate_questions(request: TechStackRequest):
    prompt = f"""
    You are a hiring assistant. Based on the following candidate information, generate exactly 3 technical interview questions.

    Name: {request.name}
    Email: {request.email}
    number: {request.number}
    Experience: {request.experience}
    Position: {request.position}
    Tech Stack: {request.tech_stack}

    Format:
    1.
    2.
    3.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=300,
        )
        questions = response.choices[0].message.content
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))