from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from pytube import YouTube
import whisper
import os
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

manual_subtitles = False

def fetch_transcript(video_link):
    global manual_subtitles
    transcript = ""

    try:
        video_id = video_link.split('=')[1]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            # Try manually created subtitles
            manual_transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
            manual_subtitles = True
            transcript = manual_transcript.fetch()
            return " ".join([item.text for item in transcript]).replace("\n", " ")

        except NoTranscriptFound:
            # Fallback to auto-generated subtitles
            generated_transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
            manual_subtitles = False
            transcript = generated_transcript.fetch()
            return " ".join([item.text for item in transcript]).replace("\n", " ")

    except (NoTranscriptFound, TranscriptsDisabled):
        # Fallback to Whisper-based transcription
        return speech_to_text(video_link)

    except VideoUnavailable:
        return "Video not found."

    except Exception as e:
        return f"An error occurred: {str(e)}"

def speech_to_text(video_link):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    yt = YouTube(video_link)
    title = yt.title.replace(" ", "_").replace("/", "_")
    audio_path = os.path.join(temp_dir, title + ".mp4")

    stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
    stream.download(output_path=temp_dir, filename=title + ".mp4")

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def transcribe_audio(youtube_url):
    return fetch_transcript(youtube_url)
