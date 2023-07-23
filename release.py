#!/usr/bin/env python3
# Removes API key
# Note: Remember to add in youtube-video-length-w-key.py in .git/info/exclude
with open('youtube-video-length-w-key.py', 'r') as file:
    lines = file.readlines()

number_of_replacements = 0
for i, line in enumerate(lines):
    str_to_match = 'api_key = '
    if str_to_match in line:
        index_api_key = line.index(str_to_match)
        lines[i] = line[:index_api_key + len(str_to_match)] + '"YOUR_YOUTUBE_API_KEY"  # Replace with your YouTube API key\n'
        number_of_replacements += 1
    if any(keyword in line for keyword in ['BETTER', 'TODO']):
        lines[i] = ''
assert number_of_replacements == 1

new_content = ''.join(lines)

with open('youtube-video-length.py', 'w') as file:
    file.write(new_content)

print("Release success")