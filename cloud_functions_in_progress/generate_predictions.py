import json

def generate_predictions(symbol, key, last_date):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET)

    blob = bucket.blob(f'models/architectures/{symbol}_models.json')
    models_params = blob.download_as_string()

    models_params = json.loads(models_params)
    models = []

    models.append(build_model(**models_params["day1"]))
    models.append(build_model(**models_params["day2"]))
    models.append(build_model(**models_params["day3"]))
    models.append(build_model(**models_params["day4"]))
    models.append(build_model(**models_params["day5"]))

    model[0].load_weights(f'gs://{BUCKET}/models/weights/{symbol}_models/day1.hdf5')
    model[1].load_weights(f'gs://{BUCKET}/models/weights/{symbol}_models/day2.hdf5')
    model[2].load_weights(f'gs://{BUCKET}/models/weights/{symbol}_models/day3.hdf5')
    model[3].load_weights(f'gs://{BUCKET}/models/weights/{symbol}_models/day4.hdf5')
    model[4].load_weights(f'gs://{BUCKET}/models/weights/{symbol}_models/day5.hdf5')

    # Read dataset and generate predictions
    predictions = ''
    #######################################

    blob = bucket.blob(f'predictions/{symbol}-{last_date}.csv')
    blob.upload_from_string(predictions, content_type='text/csv')

    return predictions