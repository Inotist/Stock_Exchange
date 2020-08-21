from os import environ as env

from tensorflow.python.lib.io import file_io
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

def build_model(request):
    params = request.get_json()
    
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

    weights_file = file_io.FileIO(f"gs://{env['BUCKET']}/models/weights/{params['symbol']}_models/{params['day']}.hdf5", mode='rb')
    temp_weights_location = f"./temp_weights_{params['day']}.hdf5"
    temp_weights_file = open(temp_weights_location, 'wb')
    temp_weights_file.write(weights_file.read())
    temp_weights_file.close()
    weights_file.close()

    model.load_weights(temp_weights_location)
    
    return model