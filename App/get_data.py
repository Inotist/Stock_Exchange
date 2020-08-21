from os import environ as env

from datetime import date
from google.cloud import storage

from generate_predictions import generate_predictions

def get_data(symbol):
    today = date.today()
    last_date = today.strftime("%Y-%m-")+str(int(today.strftime("%d"))-1)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
    
    if blob.exists(): predictions = blob.download_as_string()
    else: predictions = generate_predictions(symbol, last_date)

    return predictions