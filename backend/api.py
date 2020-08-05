from flask import Flask, request, jsonify
from requests_oauthlib import OAuth1Session
import requests, os, json, base64, pickle, nltk, re, string
from nltk.tokenize import TweetTokenizer
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get('PROJECT_API_KEY')
SECRET_TOKEN = os.environ.get('SECRET_KEY')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
SECRET_ACCESS_TOKEN = os.environ.get('SECRET_ACCESS_TOKEN')
TWEET_COUNT = 100

secret_key = f"{API_KEY}:{SECRET_TOKEN}".encode('ascii')
b64_key = base64.b64encode(secret_key)
b64_key = b64_key.decode('ascii')
classifier_file = open('tweet_classifier.pickle', 'rb')
classifier = pickle.load(classifier_file)
tt = TweetTokenizer()
stop_words = stopwords.words('english')

def removeNoise(tweetTokens, stop_words = ()):
    cleanedTokens = []
    for token, tag in pos_tag(tweetTokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)
        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith("VB"):
            pos = 'v'
        else:
            pos = 'a'
        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)
        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleanedTokens.append(token.lower())
    return cleanedTokens


@app.route("/topic", methods=['POST','GET'])
def result():
    pos_sentiment = 0
    neg_sentiment = 0
    missed_count = 0
    tweet_array = []
    time_array = []
 

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
        "count": 100,
        "lang": "en"
    }

    print("Getting Tweets.....")

    for i in range(50):
        response = requests.get(url, headers=search_headers, params=search_params)
        data = json.loads(response.content)
        for j in range(len(data["statuses"])):
            time_array.append(data["statuses"][j]["created_at"])
            tweet_array.append(data["statuses"][j]["text"])
            next_results_url_params = data['search_metadata']['next_results']
            next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
            search_params["max_id"] = next_max_id
            search_params["include_entities"] = 'true'
    
    print(len(tweet_array))

    print("Getting Sentiments.....")
    for i in range(len(tweet_array)):
        tweet = tweet_array[i]
        tweet_tokens = removeNoise(tt.tokenize(tweet), stop_words)
        tweet_sentiment = classifier.classify(dict([token, True] for token in tweet_tokens))
        if(tweet_sentiment == "Positive"):
            pos_sentiment += 1
        elif(tweet_sentiment == "Negative"):
            neg_sentiment += 1
        else:
            missed_count += 1
    
    print(f"Positive Sentiment Counter: {pos_sentiment}")
    print(f"Negative Sentiment Counter: {neg_sentiment}")
    print(f"Missed Sentiment Counter: {missed_count}")


