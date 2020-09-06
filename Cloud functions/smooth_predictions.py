# Cloud Function que reconstruye el modelo utilizado para hacer predicciones sobre predicciones y carga los pesos adecuados usando los datos almacenados en el segmento

from os import environ as env

from google.cloud import storage
import json
from pandas import read_csv
from io import BytesIO
from joblib import load
from sklearn import preprocessing
from numpy import array, append, array_str

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
    model = build_model(**models_params["full"])

    predictions = make_predictions(model, symbol, last_date)

    return array_str(predictions)

def make_predictions(model, symbol, last_date):
    data = read_csv(f'gs://{env["BUCKET"]}/datasets/{symbol}-{last_date}.csv').sort_values(by='timestamp')
    data = data.drop(columns='timestamp').to_numpy()

    # Normalise data
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])

    blob = bucket.blob(f'models/preprocessing/{symbol}_x_normaliser.joblib')
    temp_file = BytesIO()
    blob.download_to_file(temp_file)

    normaliser = load(temp_file)
    
    data = normaliser.transform(data)

    backlook = int(env["BACKLOOK"])

    days = 5

    subset = array([data[-backlook:]])
    predicted = array(model.predict(subset))

    for _ in range(days-1):
        subset = append(subset[:,1:], array([[predicted[-1]]]), axis=1)
        predicted = append(predicted, model.predict(subset), axis=0)

    predicted = normaliser.inverse_transform(predicted)

    return predicted[:,3]

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
            
    model.add(Dense(5, activation='linear'))
    
    model.compile(loss='mse', optimizer=params['optimizer'])

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(env["BUCKET"])
    blob = bucket.blob(f"models/weights/{params['symbol']}_models/{params['tag']}.hdf5")
    temp_file = BytesIO()

    # Este pequeño hack se me hizo necesario para sortear el check que "load_weights" le hace al nombre del archivo.
    def endswith(suffix, start=0, end=-1):
        return True
    temp_file.endswith = endswith

    blob.download_to_file(temp_file)

    model.load_weights(temp_file)
    
    return model