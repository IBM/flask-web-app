
from server import app

from utils import utils

@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.errorhandler(404)
@app.route("/error404")
def page_not_found(error):
    return app.send_static_file('404.html')


@app.errorhandler(500)
@app.route("/error500")
def requests_error(error):
    return app.send_static_file('500.html')

@app.after_request
def secure_headers(response):
	"""
	Apply securiy headers to the response call
	:return:
	"""
	return utils.secure_request(response)