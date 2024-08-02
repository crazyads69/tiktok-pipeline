from re import T
import crawl_data
import prepare_train
import preprocess
import asyncio
import json


def main():
    asyncio.run(crawl_data.get_trending())
    data = preprocess.load_json("/app/output/trending.json")
    processed_data = preprocess.process_data(data)
    # Save the processed data to a new file
    with open("/app/output/processed_trending.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    df = prepare_train.load_data("processed_trending.json")
    df_processed = prepare_train.process_data(df)
    df_processed.to_csv("traindata.csv", index=True)
