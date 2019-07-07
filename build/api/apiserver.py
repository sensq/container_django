from flask import Flask, jsonify, abort, make_response, render_template, request
from flask_cors import CORS
import os

api = Flask(__name__)
CORS(api)  # CORS有効化

@api.route('/add_influxdb', methods=['POST'])
def post():
    influxdb_host = os.environ.get("INFLUXDB_HOST")
    influxdb_port = os.environ.get("INFLUXDB_PORT")
    influxdb_database = os.environ.get("INFLUXDB_DB")
    
    measurement = request.form["measurement"]
    type = request.form["type"]
    ip = request.form["ip"]
    name = request.form["name"]
    from influxdb import InfluxDBClient
    client = InfluxDBClient(host=influxdb_host,
                            port=influxdb_port,
                            database=influxdb_database)
    data = [{
        "measurement": measurement,
        "tags": {"type": type},
        "fields": {
            "ip": ip,
            "name": name
        }
    }]
    result = client.write_points(data)
    print(data[0], flush=True)
    return make_response(data[0])

# Webサーバを起動する
if __name__ == '__main__':
    port = os.environ.get("APISERVER_PORT")
    from distutils.util import strtobool
    debug = strtobool(os.environ.get("APISERVER_DEBUG"))
    api.run(host='0.0.0.0', port=port, debug=debug)
