#!/usr/bin/env python3
# pip install google-api-python-client
import googleapiclient.discovery
from functools import reduce
import argparse
import re
import textwrap
import json

def iso_time_duration_to_seconds(duration_iso: str) -> int:
    #pattern = 'PT((?P<hours>\d{1,2})H)?((?P<minutes>\d{1,2})M)?((?P<seconds>\d{1,2})S)?'
    pattern = 'P((?P<days>\d{1,2})D)?(T((?P<hours>\d{1,2})H)?((?P<minutes>\d{1,2})M)?((?P<seconds>\d{1,2})S)?)?'
    prog = re.compile(pattern)
    m = prog.fullmatch(duration_iso)

    def assertion_functional():
        def check_not_zero_padded(value):
            return not (value and len(value) == 2 and value[0] == '0')
        assert all(check_not_zero_padded(m.group(part)) for part in ['days', 'hours', 'minutes', 'seconds']), [check_not_zero_padded(m.group(part)) for part in ['days', 'hours', 'minutes', 'seconds']]
    #assertion_functional()

    # Validate input duration_iso by assert not padded with 0
    def assertion():
        for part in ['days', 'hours', 'minutes', 'seconds']:
            group_value = m.group(part)
            if group_value and len(group_value) == 2:
                assert group_value[0] != '0', (part, group_value)
    #assertion()
    
    def soft_assertion():
        failed_parts = []
        for part in ['days', 'hours', 'minutes', 'seconds']:
            group_value = m.group(part)
            if group_value and len(group_value) == 2 and group_value[0] == '0':
                failed_parts.append((part, group_value))
        assert not failed_parts, failed_parts
    soft_assertion()

    D, H, M, S = m.groupdict(default=0).values()
    D, H = 0, int(H) + 24 * int(D)
    video_duration_seconds = reduce(lambda l, r: int(l)*60+int(r), (H, M, S))

    #video_duration_seconds = reduce(lambda l, r: int(l)*60+int(r), m.groupdict(default=0).values())

    assert type(video_duration_seconds) is int, type(video_duration_seconds)
    return video_duration_seconds

def search_youtube_videos():
    api_key = "YOUR_YOUTUBE_API_KEY"  # Replace with your YouTube API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    if is_list:
        videoDuration = 'any'
    else:
        # Categorize YouTube video duration
        global target_video_duration_seconds
        if not target_video_duration_seconds:
            target_video_duration_seconds = iso_time_duration_to_seconds(target_duration_iso)
        if target_video_duration_seconds < iso_time_duration_to_seconds('PT4M'):
            videoDuration = 'short'
        elif target_video_duration_seconds < iso_time_duration_to_seconds('PT20M'):
            videoDuration = 'medium'
        else:
            videoDuration = 'long'
    try:
        search_response = youtube.search().list(
            q=search_query,
            part="id,snippet",
            type="video",
            videoDuration=videoDuration,
            maxResults=maxResults  # Adjust the number of results you want to retrieve
        ).execute()
    except googleapiclient.errors.HttpError as e:
        # Error message for wrong API key
        json_ = json.loads(e.args[1])
        if json_['error']['message'] == "API key not valid. Please pass a valid API key.":
            print("Please set a valid YouTube API key in youtube-video-length.py")
            exit(1)
        else:
            raise

    hit_count = 0
    for search_result in search_response.get("items", []):
        video_id = search_result["id"]["videoId"]
        video_title = search_result["snippet"]["title"]
        duration_iso = get_video_duration(video_id, youtube)
        video_duration_seconds = iso_time_duration_to_seconds(duration_iso)

        #if is_list or duration_iso == target_duration_iso:
        if is_list or video_duration_seconds == target_video_duration_seconds:
            print_result(video_title, video_id, duration_iso, video_duration_seconds)
            hit_count += 1
    if hit_count == 0:
        print("ERROR: No match with specified filter time. Try change -q, -m arguments, or use -l to list search results without filtering by time")
        print("A search result without applying time filter:")
        print_result(video_title, video_id, duration_iso, video_duration_seconds)

def print_result(video_title, video_id, duration_iso, video_duration_seconds):
    print(f"Video Title: {video_title}")
    print(f"Video ID: {video_id}")
    print(f"Video Duration (ISO): {duration_iso}")
    print(f"Video Duration (s): {video_duration_seconds} seconds\n")

def get_video_duration(video_id, youtube):
    video_response = youtube.videos().list(
        part="contentDetails",
        id=video_id
    ).execute()

    duration_iso = video_response["items"][0]["contentDetails"]["duration"]
    return duration_iso

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description= textwrap.dedent('''
        Searches YouTube video with specified duration by YouTube Data API

        Example application of the program:
        To solve password game (https://neal.fun/password-game/) rule 24
        '''),
        formatter_class = argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group()
    # match by 2 types of time code
    group.add_argument('-i', '--iso-8601', help='ISO 8601 time duration, e.g. PT14M7S') # target_duration_iso
    group.add_argument('-s', '--seconds', help='Duration in seconds, e.g. 411', type = int) # target_duration_seconds
    #
    group.add_argument('-l', '--list', action='store_true')

    parser.add_argument('-q', '--search-query', help = 'Your desired search query, e.g. 00:14:07')

    parser.add_argument('-m', '--max-results', default=100)

    parser.add_argument('-t', '--test', action='store_true', help='Test the program')

    args = parser.parse_args()


    if args.test:
        # Real examples
        if args.list:
            args = parser.parse_args('-l -q 00:14:07'.split())
        else:
            args = parser.parse_args('-i PT14M7S -q 00:14:07'.split())
    else:
        if not args.search_query:
            parser.parse_args(['-h'])
        if not (args.iso_8601 or args.seconds or args.list):
            parser.parse_args(['-h'])

    target_duration_iso, search_query, maxResults = args.iso_8601, args.search_query, args.max_results
    target_video_duration_seconds = args.seconds
    is_list = args.list

    search_youtube_videos()
