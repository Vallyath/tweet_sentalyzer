from flask import Flask, request, jsonify
from requests_oauthlib import OAuth1Session
import requests
import os
import json
import base64
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get('PROJECT_API_KEY')
SECRET_TOKEN = os.environ.get('SECRET_KEY')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
SECRET_ACCESS_TOKEN = os.environ.get('SECRET_ACCESS_TOKEN')

secret_key = f"{API_KEY}:{SECRET_TOKEN}".encode('ascii')
b64_key = base64.b64encode(secret_key)
b64_key = b64_key.decode('ascii')

@app.route("/topic", methods=['POST','GET'])
def result():
    tweet_array = []
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    auth_url = 'https://api.twitter.com/oauth2/token'
    auth_headers = {
        "Authorization": f"Basic {b64_key}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    auth_data = {
        "grant_type": "client_credentials"
    }
    auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data) 
    access = auth_resp.json()['access_token']
    topic = request.get_json()
    print(topic)
    search_headers = {
        "Authorization": f"Bearer {access}"
    }
    search_params = {
        "q": f"{topic['topic']}",
        "count": 100
    }

    for y in range(50):
        response = requests.get(url, headers=search_headers, params=search_params)
        data = json.loads(response.content)
        tweet_array.append(data["statuses"])
        next_results_url_params = data['search_metadata']['next_results']
        next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
        search_params["max_id"] = next_max_id

    return (data)
    

