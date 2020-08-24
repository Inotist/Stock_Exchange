from os import environ as env

from datetime import date
from google.cloud import storage
from pandas import read_csv
from numpy import fromstring
import re

from get_daily_dataset import get_daily_dataset
from generate_predictions import generate_predictions

def get_data(symbol):
    today = date.today()
    last_date = today.strftime("%Y-%m-")+str(int(today.strftime("%d"))-1)

    data = read_dataset(symbol, last_date)[-30:]
    predictions = read_predictions(symbol, last_date)

    return data, predictions

def read_dataset(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'datasets/{symbol}-{last_date}.csv')

    if blob.exists():
        data = read_csv(f'gs://{env["BUCKET"]}/datasets/{symbol}-{last_date}.csv')
    else:
        data = get_daily_dataset(symbol, last_date)

    data = data.sort_values(by='timestamp').drop(columns='timestamp').to_numpy()
    
    return data

def read_predictions(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')

    if blob.exists():
        predictions = blob.download_as_string()
        predictions = predictions.decode()
    else:
        predictions = generate_predictions(symbol, last_date)

    predictions = fromstring(re.sub('[\[\]\\n]', '', predictions).strip(), dtype=float, sep=' ').reshape(30,5)

    return predictions