import base64
import os
import flask_monitoringdashboard as dashboard

from flask import Flask
# $(base64 /dev/urandom  | head -n 1 | md5sum | awk '{print $1}')
SECRET_KEY = str(base64.b64encode(bytes(os.urandom(24)))).encode()
app = Flask(__name__, template_folder="../public", static_folder="../public", static_url_path='')
app.secret_key = SECRET_KEY

from server.routes import *
from server.services import *

initServices(app)
dashboard.bind(app)

if 'FLASK_LIVE_RELOAD' in os.environ and os.environ['FLASK_LIVE_RELOAD'] == 'true':
    import livereload

    app.debug = True
    server = livereload.Server(app.wsgi_app)
    server.serve(port=os.environ['port'], host=os.environ['host'])
