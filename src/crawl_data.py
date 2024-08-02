import asyncio
import os
import dotenv
import json
import aiofiles
import random
from datetime import datetime
from TikTokApi import TikTokApi

dotenv.load_dotenv()

ms_token = os.getenv("MS_TOKEN")
if not ms_token:
    raise ValueError("MS_TOKEN not found in environment variables")
print(ms_token)

max_videos = 50000  # Reduced number of videos to collect
batch_size = 30  # Reduced batch size
min_delay = 30  # Increased minimum delay
max_delay = 60  # Increased maximum delay

# List of user agents to rotate through
user_agents = [
    # Windows Browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    # macOS Browsers
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    # Linux Browsers
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    # iOS Devices
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPod touch; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    # Android Devices
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0",
    # Other Browsers
    "Mozilla/5.0 (X11; CrOS x86_64 13904.77.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)",
]


async def get_trending():
    video_count = 0
    unique_video_ids = set()
    async with TikTokApi() as api:
        while video_count < max_videos:
            video_trending = []
            try:
                # Rotate user agents
                context_options = {
                    "viewport": {"width": 1280, "height": 1024},
                    "user_agent": random.choice(user_agents),
                }
                await api.create_sessions(
                    ms_tokens=[ms_token],  # type: ignore
                    num_sessions=1,
                    sleep_after=3,
                    context_options=context_options,
                    # proxies=proxy_urls,
                )

                trending_videos = api.trending.videos(
                    count=random.randint(10, batch_size)
                )
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
                await asyncio.sleep(120)  # Longer wait on error
                continue

            await save_trending(video_trending)
            print(f"Videos collected: {video_count}")

            # Add randomized delay between batches
            delay = random.uniform(min_delay, max_delay)
            print(f"Waiting for {delay:.2f} seconds before fetching the next batch...")
            await asyncio.sleep(delay)


async def save_trending(video_trending):
    # Change the filename to use the output folder
    output_folder = "/app/output"  # Path to the mounted output folder
    filename = os.path.join(output_folder, "trending.json")
    temp_filename = os.path.join(
        output_folder, f"trending_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    )

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
