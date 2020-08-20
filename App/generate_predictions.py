from os import environ as env

import json
from sklearn import preprocessing
from joblib import load
from tensorflow.python.lib.io import file_io
from google.cloud import storage
from pandas import read_csv
from numpy import arange, array, append, array_str

from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

from get_daily_dataset import get_daily_dataset

def generate_predictions(symbol, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    try: blob = bucket.blob(f'models/architectures/{symbol}_models.json')
    except: return f"Doesn't have a trained model for {symbol}"

    models_params = blob.download_as_string()
    
    models_params = json.loads(models_params)
    models = []

    models.append(build_model(**models_params["day1"]))
    models.append(build_model(**models_params["day2"]))
    models.append(build_model(**models_params["day3"]))
    models.append(build_model(**models_params["day4"]))
    models.append(build_model(**models_params["day5"]))

    for i in range(len(models)):
        weights_file = file_io.FileIO(f'gs://{env["BUCKET"]}/models/weights/{symbol}_models/day{i+1}.hdf5', mode='rb')
        temp_weights_location = f'./temp_weights_day{i+1}.hdf5'
        temp_weights_file = open(temp_weights_location, 'wb')
        temp_weights_file.write(weights_file.read())
        temp_weights_file.close()
        weights_file.close()

        models[i].load_weights(temp_weights_location)

    data = read_dataset(symbol, last_date)
    chunks = generate_chunks(data, models, symbol)

    predictions = array_str(chunks)

    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
    blob.upload_from_string(predictions, content_type='application/json')

    return predictions

def read_dataset(symbol, last_date):
    try:
        data = read_csv(f'gs://{env["BUCKET"]}/datasets/{symbol}-{last_date}.csv').sort_values(by='timestamp')
    except:
        data = get_daily_dataset(symbol, last_date)

    data = data.drop(columns='timestamp').to_numpy()

    # Normalise data
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'/models/preprocessing/{symbol}_x_normaliser.joblib')
    blob.download_to_filename('x_normaliser.joblib')

    x_normaliser = load('x_normaliser.joblib')
    
    return x_normaliser.transform(data)

def generate_chunks(data, models, symbol):
    # Get normaliser
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'/models/preprocessing/{symbol}_y_normaliser.joblib')
    blob.download_to_filename('y_normaliser.joblib')

    y_normaliser = load('y_normaliser.joblib')

    for i in arange(6,365,1):
        day1_sequence = array([data[-(env["BACKLOOK"]+i-1):-i+1].copy()])

        day3index = arange(len(data)-i-(env["BACKLOOK"]*3), len(data)-i, 3)
        day2index = arange(len(data)-i-(env["BACKLOOK"]*2), len(data)-i, 2)
        day4index = arange(len(data)-i-(env["BACKLOOK"]*4), len(data)-i, 4)
        day5index = arange(len(data)-i-(env["BACKLOOK"]*5), len(data)-i, 5)

        day2_sequence = array([data[day2index].copy()])
        day3_sequence = array([data[day3index].copy()])
        day4_sequence = array([data[day4index].copy()])
        day5_sequence = array([data[day5index].copy()])
        
        if i == 6:
            prediction = array([y_normaliser.inverse_transform(models[0].predict(day1_sequence)),
                                y_normaliser.inverse_transform(models[1].predict(day2_sequence)),
                                y_normaliser.inverse_transform(models[2].predict(day3_sequence)),
                                y_normaliser.inverse_transform(models[3].predict(day4_sequence)),
                                y_normaliser.inverse_transform(models[4].predict(day5_sequence))]).reshape(1,5)
            
            test_data = array([data[-i+1:,0]]).reshape(1,5)
            
        else:
            prediction = append(array([y_normaliser.inverse_transform(models[0].predict(day1_sequence)),
                                             y_normaliser.inverse_transform(models[1].predict(day2_sequence)),
                                             y_normaliser.inverse_transform(models[2].predict(day3_sequence)),
                                             y_normaliser.inverse_transform(models[3].predict(day4_sequence)),
                                             y_normaliser.inverse_transform(models[4].predict(day5_sequence))]).reshape(1,5),
                                   prediction, axis=0)

    return prediction

    

def build_model(**params):
    
    # List of parameters
    if 'density' not in params: params['density'] = int((params['lstmsize']//1.5)*2)
    if 'activation' not in params: params['activation'] = 'relu'
    if 'twice' not in params: params['twice'] = False
    if 'optimizer' not in params: params['optimizer'] = 'adam'
    if 'shuffle' not in params: params['shuffle'] = False
    
    # Model definition
    model = Sequential()
    
    model.add(LSTM(params['lstmsize'], input_shape=(92,5,), return_sequences=params['twice']))
    
    if 'dropout' in params:
        model.add(Dropout(params['dropout']))
    
    if params['twice']:
        model.add(LSTM(params['lstmsize']))
        
        if 'dropout' in params:
            model.add(Dropout(params['dropout']))
            
    model.add(Dense(params['density'], activation=params['activation']))
    
    if 'full_density' in params and params['full_density']:
        density = params['density']//2
        while density >= 12:
            model.add(Dense(density, activation=params['activation']))
            density //= 2
            
    model.add(Dense(1, activation='linear'))
    
    model.compile(loss='mse', optimizer=params['optimizer'])
    
    return model