from TikTokApi import TikTokApi
import asyncio
import os
import dotenv
import json
import aiofiles
import random
from datetime import datetime

dotenv.load_dotenv()

ms_token = os.getenv("MS_TOKEN")
if not ms_token:
    raise ValueError("MS_TOKEN not found in environment variables")
print(ms_token)

max_videos = 15000  # Number of videos to collect from TikTok trending
batch_size = 30  # Number of videos to collect per request
min_delay = 20  # Minimum delay in seconds between batches
max_delay = 40  # Maximum delay in seconds between batches


async def get_trending():
    video_count = 0
    unique_video_ids = set()
    async with TikTokApi() as api:
        try:
            await api.create_sessions(
                ms_tokens=[ms_token], num_sessions=1, sleep_after=3  # type: ignore
            )
        except Exception as e:
            print(f"Failed to create API session: {e}")
            return

        while video_count < max_videos:
            video_trending = []
            try:
                trending_videos = api.trending.videos(count=batch_size)
                async for video in trending_videos:  # type: ignore
                    if video.id not in unique_video_ids:
                        video_trending.append(video.as_dict)
                        unique_video_ids.add(video.id)
                        video_count += 1
                        if video_count >= max_videos:
                            break
                if not video_trending:
                    print("No more videos returned by the API, exiting...")
                    break
            except Exception as e:
                print(f"Error fetching trending videos: {e}")
                await asyncio.sleep(60)  # Wait longer if an error occurs
                continue

            await save_trending(video_trending)
            print(f"Videos collected: {video_count}")

            # Add randomized delay between batches
            delay = random.uniform(min_delay, max_delay)
            print(f"Waiting for {delay:.2f} seconds before fetching the next batch...")
            await asyncio.sleep(delay)


async def save_trending(video_trending):
    filename = "trending.json"
    temp_filename = f"trending_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

    try:
        if os.path.exists(filename):
            async with aiofiles.open(filename, "r") as f:
                content = await f.read()
                existing_data = json.loads(content)
        else:
            existing_data = []
    except json.JSONDecodeError:
        print("Error decoding JSON from trending.json, starting with an empty list")
        existing_data = []
    except FileNotFoundError:
        existing_data = []

    # Check for duplicates and append new data
    existing_ids = set(video["id"] for video in existing_data)
    new_videos = [video for video in video_trending if video["id"] not in existing_ids]
    existing_data.extend(new_videos)

    # Write updated data to a temporary file
    try:
        async with aiofiles.open(temp_filename, "w") as f:
            await f.write(json.dumps(existing_data, indent=4))
        # Rename the temporary file to the actual filename
        os.replace(temp_filename, filename)
    except Exception as e:
        print(f"Error writing to {filename}: {e}")


if __name__ == "__main__":
    asyncio.run(get_trending())
