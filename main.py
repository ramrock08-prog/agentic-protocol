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

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WALLET_BALANCE = 10.00

# We added 'context' here to hold the user's Resume/Profile data
class TaskRequest(BaseModel):
    prompt: str
    step: str = "init" 
    context: str = ""

@app.post("/broadcast")
def broadcast_task(req: TaskRequest):
    global WALLET_BALANCE
    logs = []
    
    # ---------------------------------------------------------
    # NEW: CAREER AUTOPILOT - SCANNING PHASE
    # ---------------------------------------------------------
    if req.step == "career_scan":
        logs.append("TRIAGE: Analyzing Resume against global opportunity databases...")
        WALLET_BALANCE -= 0.05
        
        # We force the AI to act as a Recruiter and output JSON matches
        scan_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an elite Career Matchmaker. The user wants to find jobs, internships, or hackathons based on their resume. Generate exactly 3 highly relevant simulated matches. Output ONLY valid JSON: {\"matches\": [{\"title\": \"Role Name\", \"company\": \"Company/Event Name\", \"match_score\": \"95%\"}]}"},
                {"role": "user", "content": f"Target: {req.prompt}\n\nResume/Skills: {req.context}"}
            ],
            response_format={"type": "json_object"}
        )
        
# BULLETPROOF PARSING BLOCK
        try:
            # Force the model to strict JSON response format
            response_content = scan_response.choices[0].message.content
            # Strip out any markdown blocks if the AI stubbornly adds them
            clean_content = response_content.replace('```json', '').replace('```', '').strip()
            matches_data = json.loads(clean_content)
            matches = matches_data.get("matches", [])
            
            # If the AI returned an empty list by mistake, trigger the fallback
            if not matches:
                raise ValueError("Empty matches list")
                
        except Exception as e:
            logs.append(f"> WARNING: LLM Formatting failure. Triggering hardcoded fallback schema...")
            matches = [
                {"title": "Software Engineer", "company": "TechCorp", "match_score": "90%"}, 
                {"title": "Data Analyst", "company": "Global Solutions", "match_score": "85%"}
            ]
            
        return {"status": "scanned", "logs": logs, "matches": matches, "balance": round(WALLET_BALANCE, 3)}

    # ---------------------------------------------------------
    # PHASE 1: FACTORY - DYNAMIC REQUIREMENTS GATHERING
    # ---------------------------------------------------------
    if req.step == "init":
        logs.append("TRIAGE: Analyzing problem for missing requirements...")
        pm_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Product Manager. The user has a vague problem or idea. Generate exactly 3 distinct stylistic, technical, or feature options they need to choose from before you can build it. Output ONLY valid JSON in this exact format: {\"options\": [\"Option 1\", \"Option 2\", \"Option 3\"]}"},
                {"role": "user", "content": req.prompt}
            ],
            response_format={"type": "json_object"}
        )
        try:
            options = json.loads(pm_response.choices[0].message.content).get("options", ["Standard Design", "Dark Mode", "Minimalist Light"])
        except:
            options = ["Standard", "Modern", "Classic"] 
            
        return {"status": "needs_options", "logs": logs, "options": options}

    # ---------------------------------------------------------
    # PHASE 2: EXECUTION (Factory & Career Applications)
    # ---------------------------------------------------------
    logs.append(f"TRIAGE: Finalized prompt -> '{req.prompt}'")
    p = req.prompt.lower()
    
# THE ULTIMATE AGENT MARKETPLACE
    bids = [
        # 1. The Coder (Builds UI and Software)
        {
            "name": "Agent_ProductBuilder", 
            "conf": 99 if any(w in p for w in ["website", "ui", "code", "app", "button", "login", "page", "html", "css"]) else 5, 
            "hw": "LPU-Coder", "lat": "12ms", "price": 0.15,
            "instruction": "You are a Frontend Dev. Output ONLY raw HTML and Tailwind CSS. No markdown formatting."
        },
        # 2. The Data Engineer (Builds Databases and APIs)
        {
            "name": "Agent_DataSmith", 
            "conf": 98 if any(w in p for w in ["data", "json", "database", "api", "schema"]) else 5, 
            "hw": "LPU-Logic", "lat": "9ms", "price": 0.10,
            "instruction": "You are a Data Engineer. Output ONLY a valid JSON object or array. No conversational text."
        },
        # 3. The Scholar (Solves Math and Homework)
        {
            "name": "Agent_Academic", 
            "conf": 95 if any(w in p for w in ["homework", "assignment", "essay", "math", "solve", "physics", "explain"]) else 5, 
            "hw": "LPU-Scholar", "lat": "18ms", "price": 0.05,
            "instruction": "You are a PhD-level tutor. Output a highly structured, formatted assignment or solution."
        },
        # 4. The Career Broker (Applies for Jobs)
        {
            "name": "Agent_CareerBroker", 
            "conf": 99 if any(w in p for w in ["apply", "job", "application", "cover letter", "internship", "resume"]) else 5, 
            "hw": "LPU-Negotiator", "lat": "16ms", "price": 0.20,
            "instruction": "You are an autonomous Career Agent. Formulate a highly professional application package."
        },
        # 5. The Copywriter (Writes Marketing and Social Media)
        {
            "name": "Agent_Marketer", 
            "conf": 95 if any(w in p for w in ["marketing", "email", "tweet", "sales", "pitch", "post", "blog"]) else 5, 
            "hw": "LPU-Text", "lat": "15ms", "price": 0.08,
            "instruction": "You are an expert copywriter. Output high-converting copy, formatted cleanly."
        },
        # 6. The Consultant (Builds Business Strategy)
        {
            "name": "Agent_BizAnalyst", 
            "conf": 95 if any(w in p for w in ["business", "plan", "strategy", "market", "startup", "revenue"]) else 5, 
            "hw": "LPU-Logic", "lat": "20ms", "price": 0.12,
            "instruction": "You are a startup consultant. Output a structured business plan or strategy document."
        },
        # 7. THE SAFETY NET (Handles EVERYTHING else)
        {
            "name": "Agent_Generalist", 
            # Notice the confidence is always a flat 10%. 
            # If no specialist bids 90%+, the generalist automatically wins!
            "conf": 10, 
            "hw": "LPU-Omni", "lat": "8ms", "price": 0.02,
            "instruction": "You are a helpful, general-purpose AI assistant. Answer the user's query clearly and concisely."
        }
    ]
    
    for b in bids:
        logs.append(f"NODE [{b['name']}]: {b['hw']} | {b['lat']} | Conf: {b['conf']}%")

    best_bid = max(bids, key=lambda x: x['conf'])
    logs.append(f"ROUTER: Escrow locked. Routing task to {best_bid['name']}...")
    WALLET_BALANCE -= best_bid['price']

    # We inject the Resume context into the final execution if it exists
    final_prompt = f"Request: {req.prompt}\nUser Context/Resume: {req.context}" if req.context else f"Fulfill this request exactly: {req.prompt}"

    execution = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": best_bid['instruction']},
                  {"role": "user", "content": final_prompt}]
    )
    
    return {
        "status": "complete",
        "logs": logs,
        "balance": round(WALLET_BALANCE, 3),
        "agent": best_bid['name'],
        "answer": execution.choices[0].message.content
    }