# Read the processed_trending.json file and show total length

import json
import pandas as pd
import os

json_file = "processed_trending.json"

if os.path.exists(json_file):
    with open(json_file, "r") as f:
        try:
            data = json.load(f)
            print(f"Total videos processed: {len(data)}")
        except json.decoder.JSONDecodeError as e:
            print("Error: Invalid JSON data in the file.")
else:
    print("Error: File not found.")

df = pd.read_json(json_file)

print("\nDuplicate Rows:")
print(df[df.duplicated(subset="video_id", keep=False)])
