from os import environ as env

import requests
import json
from io import BytesIO
from sklearn import preprocessing
from joblib import load
from google.cloud import storage
from pandas import read_csv
from numpy import arange, array, append, array_str

from get_daily_dataset import get_daily_dataset

def generate_predictions(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'models/architectures/{symbol}_models.json')
    if not blob.exists(): return f"Doesn't have a trained model for {symbol}"

    models_params = blob.download_as_string()
    
    models_params = json.loads(models_params)
    models = []

    models.append(requests.post(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/build_model", json=models_params["day1"]))
    models.append(requests.post(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/build_model", json=models_params["day2"]))
    models.append(requests.post(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/build_model", json=models_params["day3"]))
    models.append(requests.post(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/build_model", json=models_params["day4"]))
    models.append(requests.post(f"https://europe-west1-stock-exchange-predictions.cloudfunctions.net/build_model", json=models_params["day5"]))

    data = read_dataset(symbol, last_date)
    chunks = generate_chunks(data, models, symbol)

    predictions = array_str(chunks)

    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
    blob.upload_from_string(predictions, content_type='application/json')

    return predictions

def read_dataset(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'datasets/{symbol}-{last_date}.csv')

    if blob.exists(): data = read_csv(f'gs://{env["BUCKET"]}/datasets/{symbol}-{last_date}.csv').sort_values(by='timestamp')
    else: data = get_daily_dataset(symbol, last_date).sort_values(by='timestamp')

    data = data.drop(columns='timestamp').to_numpy()

    # Normalise data
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'models/preprocessing/{symbol}_x_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)

    x_normaliser = load(temp_file)
    
    return x_normaliser.transform(data)

def generate_chunks(data, models, symbol):
    # Get normaliser
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'models/preprocessing/{symbol}_y_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)

    y_normaliser = load(temp_file)

    backlook = int(env["BACKLOOK"])

    for i in arange(0,30,1):
        if i == 0:
            day1_sequence = array([data[-backlook:].copy()])
        else:
            day1_sequence = array([data[-(backlook+i):-i].copy()])

        day2index = arange(len(data)+1-i-(backlook*2), len(data)-i, 2)
        day3index = arange(len(data)+2-i-(backlook*3), len(data)-i, 3)
        day4index = arange(len(data)+3-i-(backlook*4), len(data)-i, 4)
        day5index = arange(len(data)+4-i-(backlook*5), len(data)-i, 5)

        day2_sequence = array([data[day2index].copy()])
        day3_sequence = array([data[day3index].copy()])
        day4_sequence = array([data[day4index].copy()])
        day5_sequence = array([data[day5index].copy()])
        
        if i == 0:
            prediction = array([y_normaliser.inverse_transform(models[0].predict(day1_sequence)),
                                y_normaliser.inverse_transform(models[1].predict(day2_sequence)),
                                y_normaliser.inverse_transform(models[2].predict(day3_sequence)),
                                y_normaliser.inverse_transform(models[3].predict(day4_sequence)),
                                y_normaliser.inverse_transform(models[4].predict(day5_sequence))]).reshape(1,5)
            
        else:
            prediction = append(array([y_normaliser.inverse_transform(models[0].predict(day1_sequence)),
                                       y_normaliser.inverse_transform(models[1].predict(day2_sequence)),
                                       y_normaliser.inverse_transform(models[2].predict(day3_sequence)),
                                       y_normaliser.inverse_transform(models[3].predict(day4_sequence)),
                                       y_normaliser.inverse_transform(models[4].predict(day5_sequence))]).reshape(1,5),
                                prediction, axis=0)

    return prediction