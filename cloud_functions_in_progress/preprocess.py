from sklearn import preprocessing
from joblib import load

def preprocess(symbol, last_date):

    try: data = pd.read_csv(f'gs://{BUCKET}/datasets/{symbol}-{last_date}.csv').sort_values(by='date')
    except: data = save_daily_dataset(symbol, key)
    data = data.drop(columns='date')

    # Sequence for the LSTM network
    backlook = 92

    # Normalise data
    normaliser = preprocessing.MinMaxScaler()
    data_norm = normaliser.fit_transform(data)

    # Y raw data
    next_day_open_values = np.array([data.to_numpy()[:,0][i + backlook] for i in range(len(data) - backlook)])
    next_day_open_values = np.expand_dims(next_day_open_values, -1)

    # Y normaliser
    y_normaliser = preprocessing.MinMaxScaler()
    y_normaliser.fit_transform(next_day_open_values)