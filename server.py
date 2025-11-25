from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🎵 AI Song Generator API Starting...")
    print(f"✓ OpenAI Key: {'Configured' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    yield

app = FastAPI(title="AI Song Generator API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class CompositionRequest(BaseModel):
    prompt: str
    bpm: Optional[int] = None
    key: Optional[str] = None
    length_bars: int = 8

class CompositionResponse(BaseModel):
    success: bool
    message: str
    composition: Optional[Dict] = None

@app.get("/")
async def root():
    return {"name": "AI Song Generator API", "version": "1.0.0", "status": "running", "openai_configured": bool(os.getenv('OPENAI_API_KEY'))}

@app.get("/health")
async def health():
    return {"status": "healthy", "openai_configured": bool(os.getenv('OPENAI_API_KEY'))}

@app.post("/generate-composition", response_model=CompositionResponse)
async def generate_composition(request: CompositionRequest):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(model="gpt-4-turbo-preview", messages=[{"role": "user", "content": f"Generate a music composition structure for: {request.prompt}"}], max_tokens=500)
        return CompositionResponse(success=True, message="Composition generated successfully", composition={"prompt": request.prompt, "bpm": request.bpm or 120, "key": request.key or "C", "ai_response": response.choices[0].message.content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
