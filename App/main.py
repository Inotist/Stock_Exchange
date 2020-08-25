from flask import Flask, render_template

from get_data import get_data

app = Flask(__name__)

@app.route('/')
@app.route('/<symbol>')
def root(symbol=None):
	from numpy import array
	data = array([118.62, 122.4, 122.68, 124.39, 126.07, 131.16, 125.9, 129.1, 126.48, 124.86, 125.82, 124.56, 123.71, 122.71, 123.5, 123.82, 126.73, 125, 123.5, 125.42, 128.76, 127.61, 125.96, 124.2, 125.25, 125, 124.83, 123.2, 123.01, 123.79])
	predictions = array([[120.83675, 119.69507, 120.08173, 119.13458, 119.48051], [123.49167, 122.585304, 122.99978, 121.87832, 122.49689], [124.32938, 123.18225, 123.72037, 122.65014, 122.83182], [125.22882, 124.46123, 124.641136, 123.82419, 124.11801], [126.260506, 125.42792, 126.10992, 125.08126, 126.172516], [126.54841, 126.27876, 128.15329, 126.937485, 128.24014], [128.94608, 127.7595, 128.2518, 127.152954, 127.94014], [127.715935, 127.77116, 128.5879, 127.35323, 128.37262], [126.34297, 126.179405, 127.26539, 126.10533, 127.03767], [126.27775, 126.20899, 126.45175, 125.86346, 126.72968], [124.76108, 124.86472, 125.53989, 125.27399, 126.49102], [125.51505, 125.492615, 126.09177, 125.17349, 126.16228], [122.879555, 122.95931, 123.41143, 122.87289, 123.96813], [122.57042, 122.63473, 122.912254, 122.2079, 123.24403], [124.05329, 123.83553, 124.11678, 123.61195, 124.204216], [125.899185, 125.374374, 125.40232, 124.8552, 124.85349], [125.59458, 125.31592, 125.81055, 125.045944, 125.61736], [126.28866, 125.74027, 125.885635, 124.975586, 124.98264], [124.97369, 124.47543, 124.18699, 123.98806, 123.87001], [126.994255, 126.45685, 126.4226, 126.01341, 126.12198], [127.46554, 127.14244, 127.73816, 127.25084, 127.3495], [126.89873, 126.50962, 126.727806, 126.22447, 126.48676], [125.30461, 125.231384, 125.48713, 124.9594, 125.10974], [125.27497, 124.9883, 125.081184, 124.75288, 124.60279], [124.61698, 124.64898, 124.536766, 124.782585, 125.25864], [124.990746, 124.78001, 125.03159, 124.75312, 125.01144], [124.15539, 124.09062, 124.45288, 124.043724, 124.26196], [123.50333, 123.24999, 123.33076, 123.17387, 123.019936], [123.19413, 123.059906, 123.004295, 122.83869, 122.99444], [125.71474, 124.96134, 125.184975, 124.72678, 124.90812]])
	return render_template('graph.html', data=data, predictions=predictions)

	if symbol:
		data, predictions = get_data(symbol)
		return render_template('graph.html', data=data, predictions=predictions)

	return render_template('index.html')

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)