from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from a URL."""
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    if hostname == "youtu.be":
        return parsed_url.path[1:]
    if hostname in ["www.youtube.com", "youtube.com", "m.youtube.com"]:
        if parsed_url.path == "/watch":
            query = parse_qs(parsed_url.query)
            if "v" in query:
                return query["v"][0]
        if parsed_url.path.startswith("/embed/"):
            return parsed_url.path.split("/")[2]
    raise ValueError("Invalid YouTube URL format")

def fetch_captions(video_url: str) -> str:
    """
    Fetch the captions (subtitles) for a YouTube video.
    Returns full transcript text or error message if unavailable.
    """
    try:
        video_id = extract_video_id(video_url)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            # Prefer manually created subtitles
            manual_transcript = transcript_list.find_manually_created_transcript(["en", "en-US", "en-GB"])
            transcript = manual_transcript.fetch()
            return " ".join([item.text for item in transcript]).replace("\n", " ")

        except NoTranscriptFound:
            # Fallback to auto-generated subtitles
            generated_transcript = transcript_list.find_generated_transcript(["en", "en-US", "en-GB"])
            transcript = generated_transcript.fetch()
            return " ".join([item.text for item in transcript]).replace("\n", " ")

    except (NoTranscriptFound, TranscriptsDisabled):
        return "No captions available for this video."
    except VideoUnavailable:
        return "Video not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    youtube_url = input("Enter YouTube URL: ").strip()
    transcript = fetch_captions(youtube_url)
    print("\nTranscription:\n")
    print(transcript)
