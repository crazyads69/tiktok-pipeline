import asyncio
import os
import dotenv
import json
import aiofiles
import random
from datetime import datetime
from TikTokApi import TikTokApi
import logging
import aiosqlite

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

dotenv.load_dotenv()

ms_token = os.getenv("MS_TOKEN")
if not ms_token:
    raise ValueError("MS_TOKEN not found in environment variables")

max_videos = 50000  # Reduced number of videos to collect
batch_size = 5  # Reduced batch size
db_path = "tiktok_videos.db"
delay_between_batches = 30  # Delay in seconds between batches
max_retries = 3  # Maximum number of retries for API calls

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


async def init_db():
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        await db.commit()


async def save_to_db(videos):
    async with aiosqlite.connect(db_path) as db:
        for video in videos:
            await db.execute(
                "INSERT OR REPLACE INTO videos (id, data) VALUES (?, ?)",
                (video["id"], json.dumps(video)),
            )
        await db.commit()


async def get_trending():
    video_count = 0
    retry_count = 0
    async with TikTokApi() as api:
        while video_count < max_videos:
            video_trending = []
            try:
                context_options = {
                    "viewport": {"width": 1280, "height": 1024},
                    "user_agent": random.choice(user_agents),
                }
                await api.create_sessions(
                    ms_tokens=[ms_token],  # type: ignore
                    num_sessions=1,
                    sleep_after=3,
                    context_options=context_options,
                )

                trending_videos = api.trending.videos(count=batch_size)
                async for video in trending_videos:  # type: ignore
                    video_trending.append(video.as_dict)
                    video_count += 1
                    if video_count >= max_videos:
                        break
                if not video_trending:
                    logging.info("No more videos returned by the API, exiting...")
                    break

                await save_to_db(video_trending)
                logging.info(f"Videos collected: {video_count}")

                # Reset retry count on successful API call
                retry_count = 0

                # Delay between batches to avoid rate limiting
                logging.info(
                    f"Waiting for {delay_between_batches} seconds before next batch..."
                )
                await asyncio.sleep(delay_between_batches)

            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    logging.error(
                        f"Max retries reached. Exiting script. Last error: {e}"
                    )
                    break
                logging.error(
                    f"Error fetching trending videos (attempt {retry_count}/{max_retries}): {e}"
                )
                wait_time = (
                    delay_between_batches * retry_count
                )  # Increasing wait time with each retry
                logging.info(f"Waiting for {wait_time} seconds before retrying...")
                await asyncio.sleep(wait_time)


async def main():
    await init_db()
    await get_trending()


if __name__ == "__main__":
    asyncio.run(main())
