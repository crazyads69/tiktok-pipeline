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
    "collected",
    "contents",
    "digged",
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
    "video",
    "vl1",
}

PROCESS_ATTRIBUTES = {
    "author",
    "authorStats",
    "createTime",
    "desc",
    "item_control",
    "music",
    "sharedEnabled",
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
    for video in data:
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
                        "author_digg": value.get("diggCount", 0),
                        "author_followers": value.get("followerCount", 0),
                        "author_following": value.get("followingCount", 0),
                        "author_heart": value.get("heart", 0),
                        "author_video": value.get("videoCount", 0),
                    }
                )
            elif key == "createTime":
                processed_video["create_time"] = datetime.datetime.utcfromtimestamp(
                    value
                ).strftime("%d-%m-%y %H:%M:%S")
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
                        "music_duration": value.get("duration", 0),
                        "album": value.get("album", ""),
                    }
                )
            elif key == "sharedEnabled":
                processed_video["share_enabled"] = value
            elif key == "statsV2":
                processed_video.update(
                    {
                        "collect_count": value.get("collectCount", 0),
                        "play_count": value.get("playCount", 0),
                        "share_count": value.get("shareCount", 0),
                        "comment_count": value.get("commentCount", 0),
                        "digg_count": value.get("diggCount", 0),
                        "repost_count": value.get("repostCount", 0),
                    }
                )
        processed_data.append(processed_video)
    return processed_data


if __name__ == "__main__":
    data = load_json("trending.json")
    processed_data = process_data(data)
    # Save the processed data to a new file
    with open("processed_trending.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    if data:
        print(data[0])
