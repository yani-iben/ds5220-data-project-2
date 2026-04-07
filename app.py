import os
import requests
import boto3
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from boto3.dynamodb.conditions import Key

API_KEY=os.getenv("TFL_API_KEY")
S3_BUCKET=os.getenv("S3_BUCKET")

API_URL= f"https://api.tfl.gov.uk/crowding/{NAPTAN_ID}/Live?app_key={API_KEY}"

def fetch_crowding_data():
    response = requests.get(API_URL)
    response.raise_for_status() # Check for 404/500 errors
    data = response.json()
    if data.get("dataAvailable"):
        value=data.get("percentageofBaseline",0)
        print(f"Crowding level: {value}%")
    else:
        print("No crowding data available at the moment.")
        
def get_data_from_dynamodb():
    dynamodb=boto3.resource('dynamodb', region_name='us-east-1')
    table=dynamodb.Table('CrowdingData')
    response = table.query(
        KeyConditionExpression=Key('station_id').eq('940GZZLUOXC')
    )
    items = response['Items']
    df=pd.DataFrame(items)
    df['datetime']= pd.to_datetime(df['timestamp'],unit='s')
    df=df.sort_values('datetime')
    return df
def create_assets(df):
    df.to_csv("crowding_data.csv",index=False)

    plt.figure(figsize=(10,6))
    plt.plot(df['datetime'], df['crowding_level'], marker='o')



