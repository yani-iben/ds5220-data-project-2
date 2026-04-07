import os
import requests
import boto3
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# 1. Setup Variables
API_KEY = os.getenv("TFL_API_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
NAPTAN_ID = os.environ.get("NAPTAN_ID", "940GZZLUVIC")
TABLE_NAME = "crowding" # Matches the table you created

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table(TABLE_NAME)

def run_pipeline():
    print(f"--- Pipeline Starting for Station: {NAPTAN_ID} ---")
    
    # 2. Fetch from TfL
    API_URL = f"https://api.tfl.gov.uk/crowding/{NAPTAN_ID}/Live?app_key={API_KEY}"
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    
    crowding_val = data.get("percentageOfBaseline", 0) # API uses capital 'O'
    crowding_decimal=Decimal(str(crowding_val)) # Convert to Decimal for DynamoDB
    timestamp = str(datetime.now().timestamp())
    
    # 3. Write to DynamoDB (The missing piece!)
    print(f"Saving {crowding_val}% to DynamoDB...")
    table.put_item(
        Item={
            'timestamp': timestamp,
            'station_id': NAPTAN_ID,
            'crowding_level': crowding_decimal
        }
    )

    # 4. Pull all data to update the graph
    print("Updating visualization...")
    response = table.scan() # Get all points for the graph
    df = pd.DataFrame(response['Items'])
    
    if not df.empty:
        df['datetime'] = pd.to_datetime(df['timestamp'].astype(float), unit='s')
        df = df.sort_values('datetime')
        
        # 5. Create Plot & CSV
        df.to_csv("crowding_data.csv", index=False)
        plt.figure(figsize=(10,6))
        plt.plot(df['datetime'], df['crowding_level'], marker='o')
        plt.title(f"Crowding Levels for {NAPTAN_ID}")
        plt.savefig("plot.png")
        
        # 6. Upload to S3
        s3 = boto3.client('s3')
        s3.upload_file("plot.png", S3_BUCKET, "plot.png", ExtraArgs={'ContentType': 'image/png'})
        print("Done! Check S3 for the new plot.")

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"ERROR: {e}")