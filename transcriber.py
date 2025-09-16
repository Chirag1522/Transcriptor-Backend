import time
import requests
import yt_dlp
import os

API_KEY = "dc9299d8ce2f41779d2a0b0828799c84"
HEADERS = {"authorization": API_KEY}
def fetch_captions(youtube_url):
    """Download audio from YouTube and return transcript and duration."""

    # 1️⃣ Extract video info (including duration)
    ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        duration_sec = info_dict.get("duration", 0)  # in seconds

    # 2️⃣ Download audio
    audio_file = "audio.mp3"
    ydl_opts["outtmpl"] = "audio.%(ext)s"
    ydl_opts["postprocessors"] = [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    # 3️⃣ Upload to AssemblyAI
    with open(audio_file, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=HEADERS,
            data=f
        )
    upload_url = response.json()["upload_url"]

    # 4️⃣ Create transcript job
    transcript_job = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers=HEADERS,
        json={"audio_url": upload_url}
    ).json()
    transcript_id = transcript_job["id"]

    # 5️⃣ Poll until completed
    while True:
        poll_resp = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=HEADERS
        ).json()
        if poll_resp["status"] == "completed":
            break
        elif poll_resp["status"] == "error":
            raise RuntimeError(f"Transcription failed: {poll_resp['error']}")
        time.sleep(5)

    # 6️⃣ Clean up local file
    if os.path.exists(audio_file):
        os.remove(audio_file)

    return poll_resp["text"], duration_sec
