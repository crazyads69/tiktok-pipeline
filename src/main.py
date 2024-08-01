from TikTokApi import TikTokApi
import asyncio
import os
import dotenv
import json

dotenv.load_dotenv()

ms_token = os.getenv("MS_TOKEN")
if not ms_token:
    raise ValueError("MS_TOKEN not found in environment variables")
print(ms_token)
max_videos = 15000  # Number of videos to collect from TikTok trending
batch_size = 30  # Number of videos to collect per request


async def get_trending():
    cursor = 0
    video_count = 0
    async with TikTokApi() as api:
        try:
            await api.create_sessions(
                ms_tokens=[ms_token], num_sessions=1, sleep_after=3
            )
        except Exception as e:
            print(f"Failed to create API session: {e}")
            return

        while video_count < max_videos:
            video_trending = []
            try:
                async for video in api.trending.videos(count=batch_size, cursor=cursor):
                    video_trending.append(video.as_dict())
                    video_count += 1
                    if video_count >= max_videos:
                        break
                if not video_trending:
                    print("No more videos returned by the API, exiting...")
                    break
            except Exception as e:
                print(f"Error fetching trending videos: {e}")
                break
            save_trending(video_trending)
            cursor += batch_size
            print(f"Cursor: {cursor}, Videos collected: {video_count}")


def save_trending(video_trending):
    # Read existing data
    try:
        if os.path.exists("trending.json"):
            with open("trending.json", "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
    except json.JSONDecodeError:
        print("Error decoding JSON from trending.json, starting with an empty list")
        existing_data = []
    except FileNotFoundError:
        existing_data = []

    # Append new data
    existing_data.extend(video_trending)

    # Write updated data
    try:
        with open("trending.json", "w") as f:
            json.dump(existing_data, f, indent=4)
    except Exception as e:
        print(f"Error writing to trending.json: {e}")


if __name__ == "__main__":
    asyncio.run(get_trending())
