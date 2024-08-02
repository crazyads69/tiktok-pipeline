import json
import datetime

# Define the attributes to skip (remove) from the data before doing any analysis
SKIP_ATTRIBUTES = {
    "AIGCDescription",
    "BAInfo",
    "adAuthorization",
    "adLabelVersion",
    "aigcLabelType",
    "challenges",
    "contents",
    "diversificationId",
    "duetDisplay",
    "duetEnabled",
    "duetInfo",
    "forFriend",
    "isAd",
    "itemCommentStatus",
    "itemMute",
    "officalItem",
    "originalItem",
    "playlistId",
    "privateItem",
    "secret",
    "showNotPass",
    "stats",
    "stitchDisplay",
    "stitchEnabled",
    "textExtra",
    "videoSuggestWordsList",
    "vl1",
}

PROCESS_ATTRIBUTES = {
    "author",
    "authorStats",
    "createTime",
    "collected",
    "digged",
    "desc",
    "id",
    "item_control",
    "music",
    "sharedEnabled",
    "video",
    "statsV2",
}


def load_json(file_path: str) -> list:
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading JSON file: {e}")
        return []


def process_data(data: list) -> list:
    processed_data = []
    total_videos = len(data)
    for index, video in enumerate(data):
        # Remove skip attributes
        video = {
            key: value for key, value in video.items() if key not in SKIP_ATTRIBUTES
        }

        # Process attributes
        processed_video = {}
        for key, value in video.items():
            if key == "author":
                processed_video.update(
                    {
                        "author_id": value.get("id", ""),
                        "author_fullname": value.get("nickname", ""),
                        "author_verified": value.get("verified", False),
                        "author_desc": value.get("signature", ""),
                        "author_nickname": value.get("uniqueId", ""),
                    }
                )
            elif key == "authorStats":
                processed_video.update(
                    {
                        "author_digg": int(value.get("diggCount", 0)),
                        "author_followers": int(value.get("followerCount", 0)),
                        "author_following": int(value.get("followingCount", 0)),
                        "author_heart": int(value.get("heart", 0)),
                        "author_video": int(value.get("videoCount", 0)),
                    }
                )
            elif key == "createTime":
                processed_video["create_time"] = datetime.datetime.utcfromtimestamp(
                    value
                ).strftime("%d-%m-%Y %H:%M:%S")
            elif key == "desc":
                processed_video["video_description"] = value.split("#")[0].strip()
                processed_video["hashtags"] = [
                    hashtag.strip()
                    for hashtag in value.split("#")[1:]
                    if hashtag.strip()
                ]
            elif key == "item_control":
                processed_video["can_repost"] = value.get("can_repost", False)
            elif key == "music":
                processed_video.update(
                    {
                        "music_id": value.get("id", ""),
                        "music_title": value.get("title", ""),
                        "music_author": value.get("authorName", ""),
                        "music_original": value.get("original", False),
                        "music_duration": int(value.get("duration", 0)),
                        "album": value.get("album", ""),
                    }
                )
            elif key == "sharedEnabled":
                processed_video["share_enabled"] = value
            elif key == "id":
                processed_video["video_id"] = value
            elif key == "collected":
                processed_video["collect_enabled"] = value
            elif key == "digged":
                processed_video["digg_enabled"] = value
            elif key == "statsV2":
                processed_video.update(
                    {
                        "collect_count": int(value.get("collectCount", 0)),
                        "play_count": int(value.get("playCount", 0)),
                        "share_count": int(value.get("shareCount", 0)),
                        "comment_count": int(value.get("commentCount", 0)),
                        "digg_count": int(value.get("diggCount", 0)),
                        "repost_count": int(value.get("repostCount", 0)),
                    }
                )
            elif key == "video":
                processed_video.update(
                    {
                        "video_height": int(value.get("height", 0)),
                        "video_width": int(value.get("width", 0)),
                        "video_duration": int(value.get("duration", 0)),
                        "video_ratio": value.get("ratio", ""),
                    }
                )
        processed_data.append(processed_video)

        if (index + 1) % 100 == 0 or (index + 1) == total_videos:
            print(f"Processed {index + 1}/{total_videos} videos")

    return processed_data


if __name__ == "__main__":
    data = load_json("output/trending.json")
    processed_data = process_data(data)
    # Save the processed data to a new file
    with open("processed_trending.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    print("Data processing complete.")
