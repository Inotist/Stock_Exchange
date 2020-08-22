from os import environ as env

import requests
import json
from io import StringIO
from google.cloud import storage

def get_daily_dataset(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob('keys.json')
    keys = blob.download_as_string()

    alpha_key = json.loads(keys)['alphavantage']

    csv = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={alpha_key}&datatype=csv')

    blob = bucket.blob(f'datasets/{symbol}-{last_date}.csv')
    blob.upload_from_string(csv.text, content_type='text/csv')
    
    return