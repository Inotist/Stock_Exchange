import webapp2

from get_data import *


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Welcome!')

    def post(self, symbol):
    	data = get_data(symbol)

        self.response.headers['Content-Type'] = 'text/plain'
    	self.response.write(data)


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)