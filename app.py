import db_access
import datetime

from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app)

connection = db_access.setup()

@app.route('/')
def hello_world():
    panel = request.args.get('panel')
    print(panel)
    doc = db_access.query(connection, datetime.datetime(2009, 11, 12, 12), int(panel))

    if doc:
        yuck_yuck(doc)
    
    # db_access.query(p, datetime.datetime(2009, 11, 12, 12), 6)
    return doc


@app.route('/delete')
def delete():
    return db_access.delete_query(connection)

@app.route('/load')
def insert():
    return db_access.insert(connection)


def yuck_yuck(doc):
    doc['_id'] = '1'
    doc['date'] = ''
    for d in doc['alternatives']:
        d['date'] = ''
        d['_id'] = ''
