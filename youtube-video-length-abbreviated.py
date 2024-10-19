
#!/usr/bin/env python3
# Abbreviated script for educational purpose
# pip install google-api-python-client
import googleapiclient.discovery
from functools import reduce
import re

def iso_time_duration_to_seconds(duration_iso: str) -> int:
    pattern = 'PT((?P<hours>\d{1,2})H)?((?P<minutes>\d{1,2})M)?((?P<seconds>\d{1,2})S)?'
    m = re.fullmatch(pattern, duration_iso)
    video_duration_seconds = reduce(lambda l, r: int(l)*60+int(r), m.groupdict(default=0).values())
    return video_duration_seconds

def search_youtube_videos(target_duration_iso, search_query, maxResults=100):
    api_key = "YOUR_YOUTUBE_API_KEY"  # Replace with your YouTube API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # Categorize YouTube video duration
    target_video_duration_seconds = iso_time_duration_to_seconds(target_duration_iso)
    if target_video_duration_seconds < iso_time_duration_to_seconds('PT4M'):
        videoDuration = 'short'
    elif target_video_duration_seconds < iso_time_duration_to_seconds('PT20M'):
        videoDuration = 'medium'
    else:
        videoDuration = 'long'
    search_response = youtube.search().list(
        q=search_query,
        part="id,snippet",
        type="video",
        videoDuration=videoDuration,
        maxResults=maxResults
    ).execute()

    for search_result in search_response.get("items", []):
        video_id = search_result["id"]["videoId"]
        video_title = search_result["snippet"]["title"]
        duration_iso = get_video_duration(video_id, youtube)
        if duration_iso == target_duration_iso:
            print(f"Video Title: {video_title}")
            print(f"Video ID: {video_id}")
            print(f"Video Duration (ISO): {duration_iso}")

def get_video_duration(video_id, youtube):
    video_response = youtube.videos().list(
        part="contentDetails",
        id=video_id
    ).execute()
    duration_iso = video_response["items"][0]["contentDetails"]["duration"]
    return duration_iso

if __name__ == "__main__":
    target_duration_iso = 'PT14M7S' # ISO 8601 time duration
    search_query = '00:14:07'
    maxResults = 100
    search_youtube_videos(target_duration_iso, search_query, maxResults)