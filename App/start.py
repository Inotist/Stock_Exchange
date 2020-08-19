import webtest

import main


def greeting():
    app = webtest.TestApp(main.app)

    response = app.get('/')

def get_symbol(symbol):
	app = webtest.TestApp(main.app)

	response = app.post('/', symbol)