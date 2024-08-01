import re
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

video_result = []


async def get_trending():
    async with TikTokApi() as api:
        try:
            await api.create_sessions(
                ms_tokens=[ms_token], num_sessions=1, sleep_after=3  # type: ignore
            )
        except Exception as e:
            print(f"Failed to create API session: {e}")
            return
        try:
            trending_videos = api.trending.videos(count=1)
            async for video in trending_videos:  # type: ignore
                video_result.append(video.as_dict)
        except Exception as e:
            print(f"Error fetching trending videos: {e}")


async def main():
    await get_trending()
    print("Waiting for 1 seconds before fetching the next video...")
    await asyncio.sleep(1)
    await get_trending()

    if len(video_result) < 2:
        print("Error: Failed to fetch two videos")
        return

    if video_result[0]["id"] != video_result[1]["id"]:
        print("Both videos are different")
        print(video_result[0]["id"])
        print(video_result[1]["id"])
        print("Test passed")
    else:
        print("Error: Both videos are the same")


if __name__ == "__main__":
    asyncio.run(main())
