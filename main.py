# main.py
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transcriber import transcribe_audio
from Summarizer import get_summary
from translator import translate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# ---------------- Transcription ----------------
@app.post("/transcribe/")
async def transcribe_endpoint(url: str = Form(...)):
    transcript = transcribe_audio(url)
    return {
        "transcript": transcript,
        "title": "Transcribed Video",
        "duration": 300
    }

# ---------------- Summarization ----------------
@app.post("/summarize/")
async def summarize_endpoint(
    text: str = Form(...),
    manual: str = Form(...),
    model_choice: str = Form(...)
):
    try:
        summary = get_summary(text, int(model_choice))
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# ---------------- Translation ----------------
@app.post("/translate/")
async def translate_endpoint(
    text: str = Form(...),
    dest: str = Form(...)
):
    try:
        translated = translate(text, dest)
        if "Translation failed:" in translated:
            raise HTTPException(status_code=400, detail=translated)
        return {"translation": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
