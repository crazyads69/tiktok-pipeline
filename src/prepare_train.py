import json
import pandas as pd
import datetime


# Define function to load processed_trending.json file and process with pandas
def load_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    return df


# Define function to process the DataFrame
def process_data(df):
    # Remove duplicates by video_id
    df = df.drop_duplicates(subset="video_id")

    # Drop records with any null values
    df = df.dropna()

    # Convert create_time to datetime format and sort from oldest to newest
    df["create_time"] = pd.to_datetime(df["create_time"], format="%d-%m-%Y %H:%M:%S")
    df = df.sort_values(by="create_time")

    return df


if __name__ == "__main__":
    df = load_data("processed_trending.json")
    print("Original DataFrame:")
    print(df.head())
    print(df.info())

    df_processed = process_data(df)
    print("\nProcessed DataFrame:")
    print(df_processed.head())
    print(df_processed.info())

    # Save the processed DataFrame to a new CSV file
    df_processed.to_csv("traindata.csv", index=False)
    print("\nData processing complete. Processed data saved to traindata.csv.")
