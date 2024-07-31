import json

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

PROCESS_ATTRIBUTES = [
    "author",
    "authorStats",
    "createTime",
    "desc",
    "item_control",
    "music",
    "statsV2",
]


def load_json(file_path: str) -> list:
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading JSON file: {e}")
        return []


def remove_attribute(data: list) -> list:
    return [
        {key: value for key, value in video.items() if key not in SKIP_ATTRIBUTES}
        for video in data
    ]


# Define function to process the attributes from the PREPROCESS_ATTRIBUTES list
# They are complex objects that need to be processed further to flatten them to a single level
def process_attribute(video: dict) -> dict:
    processed_video = {}
    for key, value in video.items():
        if key in PROCESS_ATTRIBUTES:
            if key == "author":
                processed_video["author_id"] = value.get("id", "")
                processed_video["author_nickname"] = value.get("nickname", "")
            elif key == "authorStats":
                processed_video["author_followers"] = value.get("followerCount", 0)
                processed_video["author_following"] = value.get("followingCount", 0)
                processed_video["author_heart"] = value.get("heart", 0)
            elif key == "createTime":
                processed_video["create_time"] = value
            elif key == "desc":
                processed_video["description"] = value
            elif key == "item_control":
                processed_video["comment_count"] = value.get("commentCount", 0)
                processed_video["digg_count"] = value.get("diggCount", 0)
                processed_video["share_count"] = value.get("shareCount", 0)
            elif key == "music":
                processed_video["music_id"] = value.get("id", "")
                processed_video["music_title"] = value.get("title", "")
            elif key == "statsV2":
                processed_video["play_count"] = value.get("playCount", 0)
                processed_video["share_count"] = value.get("shareCount", 0)
                processed_video["comment_count"] = value.get("commentCount", 0)
                processed_video["digg_count"] = value.get("diggCount", 0)
    return processed_video


if __name__ == "__main__":
    data = load_json("trending.json")
    cleaned_data = remove_attribute(data)
    # Save the cleaned data to a new file
    with open("cleaned_trending.json", "w") as f:
        json.dump(cleaned_data, f, indent=4)
    if data:
        print(data[0])
