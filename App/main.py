from flask import Flask, render_template

from get_data import get_data

app = Flask(__name__)

@app.route('/')
@app.route('/<symbol>')
def root(symbol=None):
	if symbol:
		data, predictions, smooth_predictions = get_data(symbol)
		if not data or not predictions or not smooth_predictions:
			return render_template('error.html', symbol=symbol)
		return render_template('graph.html', data=data, predictions=predictions, smooth_predictions=smooth_predictions, symbol=symbol)

	return render_template('index.html')

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)