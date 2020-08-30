from os import environ as env

from datetime import date
from google.cloud import storage
from pandas import read_csv
from io import BytesIO
from numpy import fromstring
import re

from get_daily_dataset import get_daily_dataset
from generate_predictions import generate_predictions, generate_smooth_predictions

def get_data(symbol):
    today = date.today()
    last_date = today.strftime("%Y-%m-")+str(int(today.strftime("%d"))-1)

    data = read_dataset(symbol, last_date)[-30:,0]
    predictions, smooth_predictions = read_predictions(symbol, last_date)

    return data, predictions, smooth_predictions

def read_dataset(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'datasets/{symbol}-{last_date}.csv')

    try:
        temp_file = BytesIO()
        blob.download_to_file(temp_file)
        data = read_csv(temp_file)
        data = data.sort_values(by='timestamp').drop(columns='timestamp').to_numpy()
    except:
        blobs = bucket.list_blobs(prefix='datasets/')
        for blob in blobs:
            blob.delete()
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
        blobs = bucket.list_blobs(prefix='predictions/')
        for blob in blobs:
            blob.delete()
        predictions = generate_predictions(symbol, last_date)

    blob = bucket.blob(f'predictions/{symbol}-{last_date}_smooth.json')

    if blob.exists():
        smooth_predictions = blob.download_as_string()
        smooth_predictions = smooth_predictions.decode()
    else:
        smooth_predictions = generate_smooth_predictions(symbol, last_date)

    predictions = fromstring(re.sub('[\[\]\\n]', '', predictions).strip(), dtype=float, sep=' ').reshape(30,5)
    smooth_predictions = fromstring(re.sub('[\[\]\\n]', '', smooth_predictions).strip(), dtype=float, sep=' ')

    return predictions, smooth_predictions