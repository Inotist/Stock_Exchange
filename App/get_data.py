# Obtengo todos los datos que mostraré en la visualización.
# Si la fecha en el nombre de los archivos está actualizada, se cargan del segmento. En caso contrario se llama a una función que se encarga de actualizar los datos.

from os import environ as env

from datetime import datetime, date, timedelta
from google.cloud import storage
from pandas import read_csv
from io import BytesIO
from numpy import fromstring
import json
import re

from get_daily_dataset import get_daily_dataset
from generate_predictions import generate_predictions, generate_smooth_predictions, generate_quarterly_predictions

def get_data(symbol):
    today = date.today()
    last_date = today - timedelta(days=1)
    last_date = last_date.strftime("%Y-%m-%d")

    data = read_dataset(symbol, last_date)[-30:,0]
    predictions, smooth_predictions, quarterly_prediction = read_predictions(symbol, last_date)

    return data, predictions, smooth_predictions, quarterly_prediction

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
        blobs = bucket.list_blobs(prefix=f'datasets/{symbol}')
        for blob in blobs:
            blob.delete()
        data = get_daily_dataset(symbol, last_date)
        if data is not None: data = data.sort_values(by='timestamp').drop(columns='timestamp').to_numpy()
    
    return data

def read_predictions(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')

    if blob.exists():
        predictions = blob.download_as_string()
        predictions = predictions.decode()
    else:
        blobs = bucket.list_blobs(prefix=f'predictions/{symbol}')
        for blob in blobs:
            blob.delete()
        predictions = generate_predictions(symbol, last_date)

    blob = bucket.blob(f'predictions/{symbol}-{last_date}_smooth.json')

    if blob.exists():
        smooth_predictions = blob.download_as_string()
        smooth_predictions = smooth_predictions.decode()
    else:
        smooth_predictions = generate_smooth_predictions(symbol, last_date)

    blobs = bucket.list_blobs(prefix=f'predictions/quarterly-{symbol}')
    updated = False
    for blob in blobs:
        if datetime.strptime(blob.name[-15:-5], '%Y-%m-%d') > datetime.strptime(last_date, '%Y-%m-%d'):
            updated = True
            break
    if updated:
        quarterly_prediction = blob.download_as_string()
        quarterly_prediction = quarterly_prediction.decode()
    else:
        blobs = bucket.list_blobs(prefix=f'predictions/quarterly-{symbol}')
        for blob in blobs:
            blob.delete()
        quarterly_prediction = generate_quarterly_predictions(symbol)

    if predictions is not None: predictions = fromstring(re.sub('[\[\]\\n]', '', predictions).strip(), dtype=float, sep=' ').reshape(30,5)
    if smooth_predictions is not None: smooth_predictions = fromstring(re.sub('[\[\]\\n]', '', smooth_predictions).strip(), dtype=float, sep=' ')
    if quarterly_prediction is not None: quarterly_prediction = json.loads(quarterly_prediction)

    return predictions, smooth_predictions, quarterly_prediction