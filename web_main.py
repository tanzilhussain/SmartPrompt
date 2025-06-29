from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core.processor import process_prompt

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

@app.get("/")
def root():
    return {"message": "SmartPrompt backend is running!"}

@app.post("/analyze")
async def analyze_prompt(data: PromptInput):
    result = process_prompt(data.prompt)
    return result