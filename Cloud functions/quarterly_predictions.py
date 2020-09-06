# Cloud Function que reconstruye el modelo utilizado para la predicción trimestral y carga los pesos adecuados usando los datos almacenados en el segmento

from os import environ as env

import requests
from datetime import datetime
from dateutil.relativedelta import *
from google.cloud import storage
import json
from pandas import read_csv, read_json, merge
from io import BytesIO, StringIO
from joblib import load
from sklearn import preprocessing

from keras.engine import Model
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, concatenate

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
    time_data, nexus_data = get_last_data(symbol)
    if time_data is None: return None

    last_clossing = nexus_data['clossingVal'].values[0]

    start_date = nexus_data['fiscalDateEnding'].values[0]
    nexus_data = nexus_data.drop(columns='fiscalDateEnding')

    destination_date = datetime.strptime(start_date, '%Y-%m-%d') + relativedelta(months=+3)
    destination_date = destination_date.strftime("%Y-%m-%d")

    # Normalise data
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'models/preprocessing/fundamental_x-time_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)
    time_normaliser = load(temp_file)

    blob = bucket.blob(f'models/preprocessing/fundamental_x-nexus_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)
    nexus_normaliser = load(temp_file)

    # Get y normaliser
    blob = bucket.blob(f'models/preprocessing/fundamental_y_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)
    y_normaliser = load(temp_file)

    time_data = time_normaliser.transform(time_data).reshape(1, 4, 100)
    nexus_data = nexus_normaliser.transform(nexus_data)
    predicted = y_normaliser.inverse_transform(model.predict([time_data, nexus_data]))

    prediction = {"start_date": start_date,
                  "last_clossing": last_clossing,
                  "destination_date": destination_date,
                  "destination_value": float(predicted[0][0])}

    return prediction

def get_last_data(symbol):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob('keys.json')
    keys = blob.download_as_string()
    alpha_key = json.loads(keys)['alphavantage']

    symbol_values = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={alpha_key}&datatype=csv')
    if symbol_values.status_code != 200: return None, None
    symbol_values = read_csv(StringIO(symbol_values.text))[['timestamp', 'close']]

    income = requests.get(f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&outputsize=full&apikey={alpha_key}')
    if income.status_code != 200: return None, None
    income = read_json(StringIO(json.dumps(json.loads(income.text)['quarterlyReports'])))
    
    balance = requests.get(f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&outputsize=full&apikey={alpha_key}')
    if balance.status_code != 200: return None, None
    balance = read_json(StringIO(json.dumps(json.loads(balance.text)['quarterlyReports'])))
    
    data = merge(income, balance, on='fiscalDateEnding')
    
    cashflow = requests.get(f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&outputsize=full&apikey={alpha_key}')
    if cashflow.status_code != 200: return None, None
    cashflow = read_json(StringIO(json.dumps(json.loads(cashflow.text)['quarterlyReports'])))
    
    data = merge(data, cashflow, on='fiscalDateEnding').sort_values(by='fiscalDateEnding')[-5:]
    data = data.replace('None', 0).fillna(0)

    for f in data['fiscalDateEnding']:
        g = f
        clossingVal = 'nan'
        while clossingVal == 'nan':
            try: clossingVal = symbol_values.loc[symbol_values['timestamp'] == g, 'close'].values[0]
            except: g = g[:-2]+str(int(g[-2:])-1)
                
            if int(f[-2:])-int(g[-2:]) > 2: return None, None
        
        data.loc[data['fiscalDateEnding'] == f, 'clossingVal'] = clossingVal

    future = None
    for f in data.sort_values(by='fiscalDateEnding', ascending=False)['fiscalDateEnding']:
        if future is not None: data.loc[data['fiscalDateEnding'] == f, 'nextClossingVal'] = future
        future = data.loc[data['fiscalDateEnding'] == f, 'clossingVal'].values[0]

    time_data = data.drop(columns=['fiscalDateEnding', 'reportedCurrency_x', 'reportedCurrency_y', 'reportedCurrency']).iloc[-5:-1]
    nexus_data = data.drop(columns=['reportedCurrency_x', 'reportedCurrency_y', 'reportedCurrency', 'nextClossingVal']).iloc[[-1]]

    return time_data, nexus_data

def build_model(**params):
    
    # List of parameters
    if 'lstmsize' not in params: params['lstmsize'] = 4
    if 'density' not in params: params['density'] = 99
    if 'merge_density' not in params: params['merge_density'] = int((params['lstmsize']//1.5)*2) + 99
    if 'activation' not in params: params['activation'] = 'relu'
    if 'twice' not in params: params['twice'] = False
    if 'optimizer' not in params: params['optimizer'] = 'adam'
    if 'shuffle' not in params: params['shuffle'] = False
        
    # Time model definition
    model_time = Sequential()
    
    model_time.add(LSTM(params['lstmsize'], input_shape=(4, 100), return_sequences=params['twice']))
    
    if 'dropout' in params:
        model_time.add(Dropout(params['dropout']))
    
    if params['twice']:
        model_time.add(LSTM(params['lstmsize']))
        
        if 'dropout' in params:
            model_time.add(Dropout(params['dropout']))
    
    # Nexus model definition
    model_nexus = Sequential()
    
    model_nexus.add(Dense(params['density'], input_shape=(99,), activation=params['activation']))
    
    # Ending pipe
    model = concatenate([model_time.output, model_nexus.output])
    
    model = Dense(params['merge_density'], activation=params['activation'])(model)
    
    if 'full_density' in params and params['full_density']:
        density = params['merge_density']//2
        while density >= 12:
            model = Dense(density, activation=params['activation'])(model)
            density //= 2
            
    model = Dense(1, activation='linear')(model)
    
    model = Model([model_time.input, model_nexus.input], model)
    
    model.compile(loss='mse', optimizer=params['optimizer'])

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f"models/weights/fundamental_quarterly/fundamental_weights.hdf5")
    temp_file = BytesIO()

    # Este pequeño hack se me hizo necesario para sortear el check que "load_weights" le hace al nombre del archivo.
    def endswith(suffix, start=0, end=-1):
        return True
    temp_file.endswith = endswith

    blob.download_to_file(temp_file)

    model.load_weights(temp_file)
    
    return model