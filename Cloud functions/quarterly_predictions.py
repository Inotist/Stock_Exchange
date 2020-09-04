from os import environ as env

import requests
from datetime import datetime
from dateutil.relativedelta import *
from google.cloud import storage
import json
from pandas import read_json, merge
from io import BytesIO, StringIO
from joblib import load
from sklearn import preprocessing

from keras.models import Sequential
from keras.layers import Dense, Dropout

def start_point(request):
    request_json = request.get_json()
    if request.args and "symbol" in request.args:
        symbol = request.args.get("symbol")
    elif request_json and "symbol" in request_json:
        symbol = request_json["symbol"]
    else:
        return f"Symbol hasn't been specified"

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f"models/architectures/fundamental_quarterly_model.json")
    if not blob.exists(): return f"Doesn't have a trained model for quarterly predictions"

    model_params = blob.download_as_string()
    model_params = json.loads(model_params)
    model = build_model(**model_params)

    prediction = predict(model, symbol)
    prediction = json.dumps(prediction)

    return prediction

def predict(model, symbol):
    data = get_last_data(symbol)
    if data is None: return None

    start_date = data['fiscalDateEnding'].values[0]
    destination_date = datetime.strptime(start_date, '%Y-%m-%d') + relativedelta(months=+3)
    destination_date = destination_date.strftime("%Y-%m-%d")

    data = data.drop(columns=['fiscalDateEnding', 'reportedCurrency_x', 'reportedCurrency_y', 'reportedCurrency'])
    data = data.replace('None', 0).fillna(0)

    # Normalise data
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'models/preprocessing/fundamental_x_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)

    x_normaliser = load(temp_file)

    # Get y normaliser
    blob = bucket.blob(f'models/preprocessing/fundamental_y_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)

    y_normaliser = load(temp_file)

    data = x_normaliser.transform(data)
    predicted = y_normaliser.inverse_transform(model.predict(data))

    prediction = {"start_date": start_date,
                  "destination_date": destination_date,
                  "growth": str(predicted[0][0])}

    return prediction

def get_last_data(symbol):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob('keys.json')
    keys = blob.download_as_string()
    alpha_key = json.loads(keys)['alphavantage']

    income = requests.get(f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&outputsize=full&apikey={alpha_key}')
    if income.status_code != 200: return None
    income = read_json(StringIO(json.dumps(json.loads(income.text)['quarterlyReports'])))
    
    balance = requests.get(f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&outputsize=full&apikey={alpha_key}')
    if balance.status_code != 200: return None
    balance = read_json(StringIO(json.dumps(json.loads(balance.text)['quarterlyReports'])))
    
    data = merge(income, balance, on='fiscalDateEnding')
    
    cashflow = requests.get(f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&outputsize=full&apikey={alpha_key}')
    if cashflow.status_code != 200: return None
    cashflow = read_json(StringIO(json.dumps(json.loads(cashflow.text)['quarterlyReports'])))
    
    data = merge(data, cashflow, on='fiscalDateEnding').sort_values(by='fiscalDateEnding', ascending=False)

    return data.iloc[[0]]

def build_model(**params):
    
    # List of parameters
    if 'density' not in params: params['density'] = x.shape[1]
    if 'activation' not in params: params['activation'] = 'relu'
    if 'optimizer' not in params: params['optimizer'] = 'adam'
    if 'shuffle' not in params: params['shuffle'] = False
    
    # Model definition
    model = Sequential()
    
    model.add(Dense(params['density'], input_shape=(98,), activation=params['activation']))
    
    density = params['density']//2
    while density >= 12:
        if 'dropout' in params:
            model.add(Dropout(params['dropout']))
        model.add(Dense(density, activation=params['activation']))
        density //= 2
            
    model.add(Dense(1, activation='linear'))
    
    model.compile(loss='mse', optimizer=params['optimizer'])

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f"models/weights/fundamental_quarterly/fundamental_weights.hdf5")
    temp_file = BytesIO()

    # I had to do this to trick the check that load_weights does to the end of the file name.
    def endswith(suffix, start=0, end=-1):
        return True
    temp_file.endswith = endswith

    blob.download_to_file(temp_file)

    model.load_weights(temp_file)
    
    return model