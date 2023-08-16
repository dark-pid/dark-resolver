import sys
import os

from flask import Flask , jsonify , render_template, send_file, abort

from api.query_api import query_api


# # PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = '.'

# templates
template_dir = os.path.join(PROJECT_ROOT,'templates')

app = Flask(__name__,template_folder=template_dir)

#basic config
app.config['JSON_AS_ASCII'] = False #utf8
app.config['JSON_SORT_KEYS'] = False #prevent sorting json

#blueprint registry
app.register_blueprint(query_api)
# app.register_blueprint(core_api_blueprint)

@app.route('/')
def index():
    return render_template('home.html')

if __name__ == "__main__":
    try:
        resolv_port=os.environ['RESOLVER_PORT']
    except KeyError:
        resolv_port=8000

    app.run(host='0.0.0.0', port=resolv_port)