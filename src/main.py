from TikTokApi import TikTokApi
import asyncio
import os
import dotenv
import json

dotenv.load_dotenv()

ms_token = os.getenv("MS_TOKEN")
print(ms_token)
max_videos = 15000  # Number of videos to collect from TikTok trending
batch_size = 30  # Number of videos to collect per request


async def get_trending():
    cursor = 0
    video_count = 0
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        while video_count < max_videos:
            video_trending = []
            async for video in api.trending.videos(count=batch_size, cursor=cursor):
                video_trending.append(video.as_dict())
                video_count += 1
                if video_count >= max_videos:
                    break
            save_trending(video_trending)
            cursor += batch_size
            print(f"Cursor: {cursor}, Videos collected: {video_count}")


def save_trending(video_trending):
    # Read existing data
    if os.path.exists("trending.json"):
        with open("trending.json", "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append new data
    existing_data.extend(video_trending)

    # Write updated data
    with open("trending.json", "w") as f:
        json.dump(existing_data, f, indent=4)


if __name__ == "__main__":
    asyncio.run(get_trending())
