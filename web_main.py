from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core.processor import process_prompt
from core.analyzer import simplify
import json
from datetime import datetime
import os, httpx
from pathlib import Path
from dotenv import load_dotenv
import tiktoken
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

LOG_PATH = Path.home() / ".smartprompt" / "prompt_log.jsonl"

@app.get("/")
def root():
    return {"message": "SmartPrompt backend is running!"}

@app.post("/analyze")
async def analyze_prompt(data: PromptInput):
    global LOG_PATH
    LOG_PATH.parent.mkdir(exist_ok=True)
    result = process_prompt(data.prompt)   
    log_entry = {
        "original prompt": result["original prompt"],
        "token count": result["token count"],
        "word count": result["word count"],
        "average word length": result["average word length"],
        "type": result["type"],
        "tone": result["tone"],
        "repetition ratio": result["repetition ratio"],
        "filler word density": result["filler word density"],
        "verbosity": result["verbosity"],
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }

    
    try:
        if LOG_PATH.exists():
            with LOG_PATH.open("r") as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    if last_entry.get("original prompt") == log_entry["original prompt"]:
                        return result  # Don't write duplicate

        with LOG_PATH.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print("Log write error:", e)

    return result
@app.get("/log")
async def get_prompt_log():
    global LOG_PATH
    try:
        if not LOG_PATH.exists():
            return []
        with LOG_PATH.open("r") as f:
            log = [json.loads(line) for line in f if line.strip()]
        return log
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@app.post("/simplify")
async def simplify_prompt(data:PromptInput):
    try:
        simplified = await simplify(data.prompt)
        return {"simplified_prompt": simplified}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))