from os import environ as env

import requests
from google.cloud import storage

def generate_predictions(symbol, last_date):
    predictions = requests.get(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/make_predictions?symbol={symbol}&last_date={last_date}").text

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
    blob.upload_from_string(predictions, content_type='text/plain')

    return predictions

def generate_smooth_predictions(symbol, last_date):
    smooth_predictions = requests.get(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/smooth_predictions?symbol={symbol}&last_date={last_date}").text

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'predictions/{symbol}-{last_date}_smooth.json')
    blob.upload_from_string(predictions, content_type='text/plain')