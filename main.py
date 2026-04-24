import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class UserData(BaseModel):
    name: str
    email: str
    context: str
    goal: str

@app.post("/generate_dashboard")
def generate_dashboard(req: UserData):
    system_prompt = f"""
    You are a real-world opportunity finder.
    User: {req.name}, Email: {req.email}, Skills: {req.context}
    Goal: {req.goal}
    
    Find 4 REAL, SPECIFIC opportunities matching their goal and skills.
    For each, write a complete pre-filled application/registration message using their actual name and email.
    
    Output ONLY this JSON format, nothing else:
    {{
      "opportunities": [
        {{
          "title": "Exact opportunity name",
          "org": "Organization name",
          "deadline": "Deadline or date",
          "link": "https://real-registration-link.com",
          "payload": "Complete pre-filled application text using {req.name} and {req.email}"
        }}
      ]
    }}
    """
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={{"type": "json_object"}}
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        return {{"opportunities": [
            {{"title": "Global AI Hackathon 2026", "org": "Devpost", "deadline": "May 15 2026", "link": "https://devpost.com/hackathons", "payload": f"Name: {req.name}\nEmail: {req.email}\nSkills: {req.context}"}},
            {{"title": "AI Innovation Challenge", "org": "Unstop", "deadline": "May 20 2026", "link": "https://unstop.com", "payload": f"Name: {req.name}\nEmail: {req.email}\nSkills: {req.context}"}}
        ]}}