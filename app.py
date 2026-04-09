import os
import requests
import boto3
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# 1. Setup Variables (Using os.getenv ensures it doesn't crash if missing)
API_KEY = os.getenv("TFL_API_KEY")
S3_BUCKET = os.getenv("S3_BUCKET", "ds5220project2") # Default to your bucket name
NAPTAN_ID = os.environ.get("NAPTAN_ID", "940GZZLUVIC")
TABLE_NAME = "crowding" 

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client('s3')

def run_pipeline():
    print(f"--- Pipeline Starting for Station: {NAPTAN_ID} ---")
    
    # 2. Fetch from TfL
    API_URL = f"https://api.tfl.gov.uk/crowding/{NAPTAN_ID}/Live?app_key={API_KEY}"
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    
    crowding_val = data.get("percentageOfBaseline", 0)
    crowding_decimal = Decimal(str(crowding_val)) 
    timestamp = str(datetime.now().timestamp())
    
    # 3. Write to DynamoDB
    print(f"Saving {crowding_val}% to DynamoDB...")
    table.put_item(
        Item={
            'timestamp': timestamp,
            'station_id': NAPTAN_ID,
            'crowding_level': crowding_decimal
        }
    )

    # 4. Pull all data to update the graph (This gets your 72-hour history)
    print("Updating visualization from DynamoDB history...")
    response = table.scan() 
    df = pd.DataFrame(response['Items'])
    
    if not df.empty:
        # Convert timestamp string -> float -> datetime
        df['datetime'] = pd.to_datetime(df['timestamp'].astype(float), unit='s')
        df = df.sort_values('datetime')
        
        # 5. Create Plot & CSV locally
        df.to_csv("crowding_data.csv", index=False)
        
        plt.figure(figsize=(10,6))
        plt.plot(df['datetime'], df['crowding_level'].astype(float), marker='o')
        plt.title(f"Crowding Levels for {NAPTAN_ID}")
        plt.xlabel("Time")
        plt.ylabel("Crowding %")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("plot.png")
        
        # 6. Upload to S3 (The "Last Line" fix)
        print(f"Uploading to S3 Bucket: {S3_BUCKET}...")
        s3.upload_file("crowding_data.csv", S3_BUCKET, "crowding_data.csv")
        s3.upload_file("plot.png", S3_BUCKET, "plot.png", 
                       ExtraArgs={'ContentType': 'image/png'})
        print("Done! Check your S3 Website URL.")

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"ERROR: {e}")