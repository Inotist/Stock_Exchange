import json
from sklearn import preprocessing
from joblib import load
from tensorflow.python.lib.io import file_io
from google.cloud import storage
import pandas as pd
import numpy as np

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

from get_daily_dataset import *

BACKLOOK = 92

def generate_predictions(symbol, bucket_name, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

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
        weights_file = file_io.FileIO(f'gs://{bucket_name}/models/weights/{symbol}_models/day{i+1}.hdf5', mode='rb')
        temp_weights_location = f'./temp_weights_day{i+1}.hdf5'
        temp_weights_file = open(temp_weights_location, 'wb')
        temp_weights_file.write(weights_file.read())
        temp_weights_file.close()
        weights_file.close()

        models[i].load_weights(temp_weights_location)

    data = read_dataset(symbol, bucket_name, last_date)
    chunks = generate_chunks(data, models, symbol, bucket_name)

    predictions = np.array_str(chunks)

    blob = bucket.blob(f'predictions/{symbol}-{last_date}.json')
    blob.upload_from_string(predictions, content_type='application/json')

    return predictions

def generate_chunks(data, models, symbol, bucket_name):
    # Get normaliser
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(f'/models/preprocessing/{symbol}_y_normaliser.joblib')
    blob.download_to_filename('y_normaliser.joblib')

    y_normaliser = load('y_normaliser.joblib')

    for i in np.arange(6,365,1):
        day1_sequence = np.array([data[-(BACKLOOK+i-1):-i+1].copy()])

        day2index = np.arange(len(data)-i-(BACKLOOK*2), len(data)-i, 2)
        day3index = np.arange(len(data)-i-(BACKLOOK*3), len(data)-i, 3)
        day4index = np.arange(len(data)-i-(BACKLOOK*4), len(data)-i, 4)
        day5index = np.arange(len(data)-i-(BACKLOOK*5), len(data)-i, 5)

        day2_sequence = np.array([data[day2index].copy()])
        day3_sequence = np.array([data[day3index].copy()])
        day4_sequence = np.array([data[day4index].copy()])
        day5_sequence = np.array([data[day5index].copy()])
        
        if i == 6:
            prediction = np.array([y_normaliser.inverse_transform(models[0].predict(day1_sequence)),
                                   y_normaliser.inverse_transform(models[1].predict(day2_sequence)),
                                   y_normaliser.inverse_transform(models[2].predict(day3_sequence)),
                                   y_normaliser.inverse_transform(models[3].predict(day4_sequence)),
                                   y_normaliser.inverse_transform(models[4].predict(day5_sequence))]).reshape(1,5)
            
            test_data = np.array([data[-i+1:,0]]).reshape(1,5)
            
        else:
            prediction = np.append(np.array([y_normaliser.inverse_transform(models[0].predict(day1_sequence)),
                                             y_normaliser.inverse_transform(models[1].predict(day2_sequence)),
                                             y_normaliser.inverse_transform(models[2].predict(day3_sequence)),
                                             y_normaliser.inverse_transform(models[3].predict(day4_sequence)),
                                             y_normaliser.inverse_transform(models[4].predict(day5_sequence))]).reshape(1,5),
                                   prediction, axis=0)

    return prediction

def read_dataset(symbol, bucket_name, last_date):
    try:
        data = pd.read_csv(f'gs://{bucket_name}/datasets/{symbol}-{last_date}.csv').sort_values(by='timestamp')
    except:
        data = get_daily_dataset(symbol, bucket_name, last_date)

    data = data.drop(columns='timestamp').to_numpy()

    # Normalise data
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(f'/models/preprocessing/{symbol}_x_normaliser.joblib')
    blob.download_to_filename('x_normaliser.joblib')

    x_normaliser = load('x_normaliser.joblib')
    
    return x_normaliser.transform(data)

    

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