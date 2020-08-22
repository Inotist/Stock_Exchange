from os import environ as env

import requests
from google.cloud import storage
from pandas import read_csv
from numpy import fromstring
import re

from get_daily_dataset import get_daily_dataset

def generate_predictions(symbol, last_date):
    data = read_dataset(symbol, last_date)
    predictions = requests.post(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/build_model_and_predict?symbol={symbol}&last_date={last_date}").text
    predictions = np.fromstring(re.sub('[\[\]\\n]', '', predictions).strip(), dtype=float, sep=' ').reshape(30,5)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
    blob.upload_from_string(predictions, content_type='application/json')

    return data, predictions

def read_dataset(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'datasets/{symbol}-{last_date}.csv')

    if blob.exists(): data = read_csv(f'gs://{env["BUCKET"]}/datasets/{symbol}-{last_date}.csv').sort_values(by='timestamp')
    else: data = get_daily_dataset(symbol, last_date).sort_values(by='timestamp')

    data = data.drop(columns='timestamp').to_numpy()
    
    return data