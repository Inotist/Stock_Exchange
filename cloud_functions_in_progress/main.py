import requests
from datetime import date
from google.cloud import storage

BUCKET = 'sep_files'

def get_data(request):
    if request.args and 'key' in request.args:
        alpha_key = request.args.get('key')
    elif request_json and 'key' in request_json:
        alpha_key = request_json['key']
    else:
        return 'You need an api key for Alpha Vantage'

    if request.args and 'symbol' in request.args:
        symbol = request.args.get('symbol')
    elif request_json and 'symbol' in request_json:
        symbol = request_json['symbol']
    else:
        return 'You must specify a symbol from the stock marquet'
        
    today = date.today()
    last_date = today.strftime("%Y-%m-")+str(int(today.strftime("%d"))-1)

    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET)
        blob = bucket.blob(f'predictions/{symbol}_{last_date}.json')
        predictions = blob.download_as_string()

    except:
        predictions = generate_predictions(symbol, key, last_date)

    return predictions