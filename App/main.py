from flask import Flask, render_template

from get_data import get_data

app = Flask(__name__)

@app.route('/')
@app.route('/<symbol>')
def root(symbol=None):
	if symbol:
		#data, predictions, smooth_predictions, quarterly_prediction = get_data(symbol)

		data = [129.1, 126.48, 124.86, 125.82, 124.56, 123.71, 122.71, 123.5, 123.82, 126.73, 125, 123.5, 125.42, 128.76, 127.61, 125.96, 124.2, 125.25, 125, 124.83, 123.2, 123.01, 123.79, 126, 124.95, 124.6, 124.96, 125.25, 122.85, 123.72]
		predictions = [[127.61189, 127.46299, 127.550186, 127.60333, 128.0851], [126.12754, 126.09655, 127.03521, 126.400085, 126.50137], [125.94492, 125.4409, 126.41907, 126.07832, 126.345634], [124.57041, 124.523834, 126.50275, 125.63613, 125.40982], [125.075584, 124.677574, 126.074196, 125.48422, 125.73414], [122.34649, 122.45073, 124.29816, 123.29372, 123.2591], [121.93938, 121.99682, 123.58755, 122.32547, 122.58], [123.328766, 123.07037, 124.12876, 123.768074, 123.896545], [125.05574, 124.54165, 124.45475, 124.69754, 124.65137], [124.979996, 124.72427, 124.51679, 125.07963, 125.21154], [125.488884, 125.21895, 124.47715, 124.558655, 124.90488], [124.10949, 123.88606, 123.85939, 123.79456, 123.68939], [126.238, 125.90497, 125.14923, 125.65902, 126.11537], [126.95566, 126.6223, 126.16192, 127.29381, 127.152954], [126.23413, 126.11124, 125.37936, 126.19254, 126.13625], [124.773544, 124.79341, 124.79527, 125.00627, 124.78008], [124.65004, 124.489006, 124.678604, 124.61616, 124.39852], [124.221375, 124.0662, 124.549065, 125.05175, 124.72129], [124.49181, 124.2637, 124.124, 124.80768, 124.57947], [123.690056, 123.44495, 123.51518, 124.234146, 123.7766], [122.974884, 122.77754, 123.00833, 123.14415, 122.63493], [122.637726, 122.37257, 122.38003, 122.85737, 122.59583], [124.95493, 124.18372, 123.32953, 124.29511, 124.75378], [124.7828, 124.19911, 123.76058, 125.008545, 124.60592], [123.95806, 123.73577, 122.73426, 123.85969, 123.618164], [124.192825, 123.82299, 123.21867, 123.864395, 123.69366], [124.50844, 124.14614, 123.757614, 124.542114, 124.18132], [123.069176, 122.96414, 122.650215, 123.948494, 123.62454], [122.899826, 122.592705, 122.24061, 122.82953, 122.7424], [127.16593, 125.837524, 124.62162, 125.2232, 126.44975]]
		smooth_predictions = [127.20398, 126.97301, 126.6073, 126.11497, 125.55416]
		quarterly_prediction = {"start_date": "2020-06-30", "destination_date": "2020-09-30", "destination_value": "73.532616"}

		if data is None or predictions is None or smooth_predictions is None or quarterly_prediction is None:
			return render_template('error.html', symbol=symbol)
		return render_template('graph.html', data=data, predictions=predictions, smooth_predictions=smooth_predictions, quarterly_prediction=quarterly_prediction, symbol=symbol)

	return render_template('index.html')

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)