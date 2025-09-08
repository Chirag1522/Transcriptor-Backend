from transformers import pipeline
import unicodedata
import logging

# Optional: suppress unnecessary logs
logging.getLogger("transformers").setLevel(logging.ERROR)

# Use fast and lightweight summarization model
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

# Initialize the pipeline globally (loads only once)
summarizer_pipeline = pipeline("summarization", model=MODEL_NAME, tokenizer=MODEL_NAME)

def get_summary(text: str, model_choice: int = 0) -> str:
    try:
        # Limit length to ~3000 characters to avoid timeout
        if len(text) > 3000:
            text = text[:3000]

        summary = summarizer_pipeline(
            text,
            max_length=130,
            min_length=30,
            do_sample=False
        )[0]["summary_text"]

        return clean_summary(summary)
    except Exception as e:
        return f"Error: {str(e)}"

def clean_summary(text: str) -> str:
    irrelevant = ["[music]", "[Music]", "<<", ">>", "\n"]
    for item in irrelevant:
        text = text.replace(item, "")
    cleaned = text.strip()
    normalized = unicodedata.normalize("NFKD", cleaned)
    return normalized.encode("ascii", "ignore").decode("ascii")
