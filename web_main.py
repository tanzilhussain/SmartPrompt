from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core.processor import process_prompt
from core.analyzer import simplify
import json
import datetime
import os, httpx
from dotenv import load_dotenv
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptInput(BaseModel):
    prompt: str

LOG_PATH = "data/prompt_log.jsonl"

@app.get("/")
def root():
    return {"message": "SmartPrompt backend is running!"}

@app.post("/analyze")
async def analyze_prompt(data: PromptInput):
    result = process_prompt(data.prompt)

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps({
        "prompt": data.prompt,
        "type": result["type"],
        "tone": result["tone"],
        "verbosity": result["verbosity"],
        "word_count": result["word count"],
        "repetition_ratio": result["repetition ratio"],
        "filler_word_density": result["filler word density"],
        "simplified_prompt": result["simplified_prompt"],
        "timestamp": datetime.utcnow().isoformat(),
    }) + "\n")
    return result

@app.get("/log")
async def get_prompt_log():
    logs = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs

@app.post("/simplify")
async def simplify_prompt(data:PromptInput):
    try:
        simplified = await simplify(data.prompt)
        return {"simplified_prompt": simplified}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))