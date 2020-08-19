import requests
from datetime import date
from google.cloud import storage

from generate_predictions import *

BUCKET = 'sep_files'

def get_data(symbol):
    today = date.today()
    last_date = today.strftime("%Y-%m-")+str(int(today.strftime("%d"))-1)

    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET)
        blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
        predictions = blob.download_as_string()

    except:
        predictions = generate_predictions(symbol, BUCKET, last_date)

    return predictions