from os import environ as env

from google.cloud import storage
import json
from pandas import read_csv
from io import BytesIO
from joblib import load
from sklearn import preprocessing
from numpy import arange, array, append, array_str

from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

def start_point(request):
    request_json = request.get_json()
    if request.args and "symbol" in request.args:
        symbol = request.args.get("symbol")
    elif request_json and "symbol" in request_json:
        symbol = request_json["symbol"]
    else:
        return f"Symbol hasn't been specified"
        
    if request.args and "last_date" in request.args:
        last_date = request.args.get("last_date")
    elif request_json and "last_date" in request_json:
        last_date = request_json["last_date"]
    else:
        return f"Date hasn't been specified"

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f"models/architectures/{symbol}_models.json")
    if not blob.exists(): return f"Doesn't have a trained model for {symbol}"

    models_params = blob.download_as_string()
    models_params = json.loads(models_params)
    models = []

    models.append(build_model(**models_params["day1"]))
    models.append(build_model(**models_params["day2"]))
    models.append(build_model(**models_params["day3"]))
    models.append(build_model(**models_params["day4"]))
    models.append(build_model(**models_params["day5"]))

    predictions = make_predictions(models, symbol, last_date)

    return array_str(predictions)

def make_predictions(models, symbol, last_date):
    data = read_csv(f'gs://{env["BUCKET"]}/datasets/{symbol}-{last_date}.csv').sort_values(by='timestamp')
    data = data.drop(columns='timestamp').to_numpy()

    # Normalise data
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'models/preprocessing/{symbol}_x_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)

    x_normaliser = load(temp_file)
    
    data = x_normaliser.transform(data)

    # Get y normaliser
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

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f"models/weights/{params['symbol']}_models/{params['tag']}.hdf5")
    temp_file = BytesIO()

    # I had to do this to trick the check that load_weights does to the end of the file name.
    def endswith(suffix, start=0, end=-1):
        return True
    temp_file.endswith = endswith

    blob.download_to_file(temp_file)

    model.load_weights(temp_file)
    
    return model