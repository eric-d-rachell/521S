from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send, emit
from flask_pymongo import PyMongo
from dateutil.parser import parse
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = ##REDACT##
app.config["MONGO_URI"] = ##REDACT##
mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('connect')
def connected():
    emit('connected',  {'OK':200})
    return ({"OK":200})


@app.route('/diagnostic')
def diagnostic():
    return ({"OK":200})


@app.route('/pub', methods=['POST'])
def publish():
    socketio.emit('publish', json.dumps(request.json))
    return ({"OK":200})

@app.route('/collection', methods=['GET'])
def collection():

    collections = mongo.db.list_collection_names()
    for idx,key in enumerate(collections):
        if key == 'obdVTC' or key == "0123456789AFCDEF":
            collections.pop(idx)

    response = jsonify({"collections": collections})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/histories/<vin>', methods=['GET'])
def histories(vin):

    collection = mongo.db[vin]
    cursor = collection.find({}, {'_id': 0, 'packetNumber':0})
    current_hash = ''
    routes_dict = {'data':[]}
    current_route_list = []
    current_route_time = ""
    for document in cursor:
        if document['hash'] != current_hash: # new route
            # build history object
            if len(current_route_list) != 0:
                h = {}
                rawstamp = parse(str(current_route_list[0]['timestamp']))
                adjstamp = rawstamp.replace(hour=(rawstamp.hour - 6))
                h['start_time'] = datetime.strftime(adjstamp, "%A %d %b %Y %I:%M %p")
                h['route_data'] = current_route_list
                routes_dict['data'].append(h)

            # clear old route data
            current_hash = document['hash']
            current_route_list = []
            current_route_time = document['timestamp']

        else:
            current_route_list.append(document)

    response = jsonify(routes_dict)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
