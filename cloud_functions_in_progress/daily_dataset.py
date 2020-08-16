from io import StringIO
import pandas as pd

def save_daily_dataset(symbol, key, last_date):
    csv = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={alpha_key}&datatype=csv')
    data = pd.read_csv(StringIO(csv.text))

    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET)
        blob = bucket.blob(f'datasets/{symbol}-{last_date}.csv')
        blob.upload_from_string(csv.text, content_type='text/csv')

    except: return None
    
    return data