# Genero las predicciones usando Cloud Functions y las almaceno en el segmento indicando la fecha a la que corresponden

from os import environ as env

import requests
import json
from google.cloud import storage

def generate_predictions(symbol, last_date):
    predictions = requests.get(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/make_predictions?symbol={symbol}&last_date={last_date}")
    if predictions.status_code != 200: return None
    predictions = predictions.text

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
    blob.upload_from_string(predictions, content_type='text/plain')

    return predictions

def generate_smooth_predictions(symbol, last_date):
    smooth_predictions = requests.get(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/smooth_predictions?symbol={symbol}&last_date={last_date}")
    if smooth_predictions.status_code != 200: return None
    smooth_predictions = smooth_predictions.text

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f'predictions/{symbol}-{last_date}_smooth.json')
    blob.upload_from_string(smooth_predictions, content_type='text/plain')

    return smooth_predictions

def generate_quarterly_predictions(symbol):
    prediction = requests.get(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/quarterly_predictions?symbol={symbol}")
    if prediction.status_code != 200: return None
    prediction = prediction.text

    destination_date = json.loads(prediction)['destination_date']

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f"predictions/quarterly-{symbol}-{destination_date}.json")
    blob.upload_from_string(prediction, content_type='text/plain')

    return prediction