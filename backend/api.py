from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route("/topic", methods=['POST','GET'])
def result():
    result1 = request.get_json(force=True)
    print(result1)
    return jsonify(result1) 
