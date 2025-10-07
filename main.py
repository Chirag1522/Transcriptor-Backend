# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transcriber import fetch_captions
from Summarizer import get_summary   # ensure filename matches lowercase
from translator import translate


app = FastAPI()

# 1. Define the allowed origins
origins = [
    # Allow your specific frontend domain
    "https://transcriptor-frontend-1.onrender.com",
    # If you also develop locally, you might include the local host
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# 2. Add the CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Specifies which origins are allowed
    allow_credentials=True,             # Allow cookies to be included in requests
    allow_methods=["*"],                # Allow all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],                # Allow all headers
)

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# ---------------- Transcription ----------------
@app.post("/transcribe/")
async def transcribe_endpoint(url: str = Form(...)):
    try:
        transcript, duration = fetch_captions(url)
        return {
            "transcript": transcript,
            "title": "Transcribed Video",
            "duration": duration
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# ---------------- Summarization ----------------
@app.post("/summarize/")
async def summarize_endpoint(
    text: str = Form(...),
    manual: str = Form(...),        # compatibility
    model_choice: str = Form(...),  # compatibility
):
    try:
        summary = get_summary(text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# ---------------- Translation ----------------
@app.post("/translate/")
async def translate_endpoint(
    text: str = Form(...),
    dest: str = Form(...),
):
    try:
        translated = translate(text, dest)
        if "Translation failed:" in translated:
            raise HTTPException(status_code=400, detail=translated)
        return {"translation": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/transcribe_test/")
def transcribe_test(url: str):
    transcript, duration = fetch_captions(url)
    return {
        "transcript": transcript,
        "title": "Transcribed Video",
        "duration": duration
    }
