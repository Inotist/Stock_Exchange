import json
from io import StringIO
from google.cloud import storage
import pandas as pd

def get_daily_dataset(symbol, bucket_name, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob('keys.json')
    keys = blob.download_as_string()

    alpha_key = json.loads(keys)['alphavantage']

    csv = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={alpha_key}&datatype=csv')
    data = pd.read_csv(StringIO(csv.text))

    blob = bucket.blob(f'datasets/{symbol}-{last_date}.csv')
    blob.upload_from_string(csv.text, content_type='text/csv')
    
    return data