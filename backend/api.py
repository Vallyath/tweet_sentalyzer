from flask import Flask, request, jsonify
from requests_oauthlib import OAuth1Session
import requests, os, json, base64, pickle, nltk, re, string, calendar, datetime
import matplotlib.pyplot as plt
import numpy as np
from nltk.tokenize import TweetTokenizer
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from flask_cors import CORS
app = Flask(__name__, static_folder='./build', static_url_path='/')
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

@app.route('/')
def index():
    return app.send_static_file('index.html')

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
    pos_dict = {}
    neg_dict = {}
    pos_time = {}
    neg_time = {}
    all_time = {}
    all_dates = []
    pos_sorted = {}
    neg_sorted = {}
    all_sorted = {}
    dates = []
    sentiments = []

    months = {v: k for k,v in enumerate(calendar.month_abbr)}

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
            time_array.append(data["statuses"][j]["created_at"][4:11] + data["statuses"][j]["created_at"][26:30])
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
            if time_array[i] in pos_dict:
                pos_dict[time_array[i]] += 1
            else:
                pos_dict[time_array[i]] = 1
        elif(tweet_sentiment == "Negative"):
            neg_sentiment += 1
            if time_array[i] in neg_dict:
                neg_dict[time_array[i]] -= 1
            else:
                neg_dict[time_array[i]] = -1
        else:
            missed_count += 1
    
    print(f"Positive Sentiment Counter: {pos_sentiment}")
    print(f"Negative Sentiment Counter: {neg_sentiment}")
    print(f"Missed Sentiment Counter: {missed_count}")

    for key in pos_dict:
        pos_time[f"{months[key[:3]]}-{key[4:6]}-{key[7:11]}"] = pos_dict[key]
    
    for key in neg_dict:
        neg_time[f"{months[key[:3]]}-{key[4:6]}-{key[7:11]}"] = neg_dict[key]


    #combine the two arrays right now to sort 
    #sort the two 
    pos_dates = [datetime.datetime.strptime(key, '%m-%d-%Y') for key in pos_time]
    neg_dates = [datetime.datetime.strptime(key, '%m-%d-%Y') for key in neg_time]
    pos_set = set(pos_dates)
    neg_set = set(neg_dates)
    diff = neg_set - pos_set
    all_dates = pos_dates + list(diff)
    all_dates.sort()
    print(all_dates)
    sorted_all_dates = [datetime.datetime.strftime(dates, '%m-%d-%Y') for dates in all_dates]
    #think of all edge cases
    for i in range(len(sorted_all_dates)):
        if(sorted_all_dates[i][1:] in pos_time and sorted_all_dates[i][1:] in neg_time):
            all_sorted[sorted_all_dates[i]] = pos_time[sorted_all_dates[i][1:]] + neg_time[sorted_all_dates[i][1:]]
            total = pos_time[sorted_all_dates[i][1:]] + -(neg_time[sorted_all_dates[i][1:]])
            sentiment = (pos_time[sorted_all_dates[i][1:]] + neg_time[sorted_all_dates[i][1:]])/total
            if(sorted_all_dates[i] not in dates):
                dates.append(sorted_all_dates[i])
                sentiments.append(sentiment)
        elif(sorted_all_dates[i] in pos_time and sorted_all_dates[i] in neg_time):
            all_sorted[sorted_all_dates[i]] = pos_time[sorted_all_dates[i]] + neg_time[sorted_all_dates[i]]
            total = pos_time[sorted_all_dates[i]] + -(neg_time[sorted_all_dates[i]])
            sentiment = (pos_time[sorted_all_dates[i]] + neg_time[sorted_all_dates[i]])/total
            if(sorted_all_dates[i] not in dates):
                dates.append(sorted_all_dates[i])
                sentiments.append(sentiment)
        elif(sorted_all_dates[i][1:] in pos_time or sorted_all_dates[i] in pos_time and (sorted_all_dates[i][1:] not in neg_time or sorted_all_dates[i] not in neg_time)):
            if(sorted_all_dates[i][1:] in pos_time):
                #possible that the first line can be skipped entirely seems unnecessary
                all_sorted[sorted_all_dates[i]] = pos_time[sorted_all_dates[i][1:]]
            elif(sorted_all_dates[i] in pos_time):
                all_sorted[sorted_all_dates[i]] = pos_time[sorted_all_dates[i]]
            #because there are no negative sentiments on this day that means that there is nothing to
            #lower the amount of sentiment with so the sentiment is completely positive on this day
            if(sorted_all_dates[i] not in dates):
                dates.append(sorted_all_dates[i])
                sentiments.append(1)
        elif(sorted_all_dates[i][1:] in neg_time or sorted_all_dates[i] in neg_time and(sorted_all_dates[i][1:] not in pos_time or sorted_all_dates[i] not in pos_time)):
            if(sorted_all_dates[i][1:] in neg_time):
                #possible that the first line can be skipped entirely seems unnecessary
                all_sorted[sorted_all_dates[i]] = neg_time[sorted_all_dates[i][1:]]
            elif(sorted_all_dates[i] in neg_time):
                all_sorted[sorted_all_dates[i]] = neg_time[sorted_all_dates[i]]
            if(sorted_all_dates[i] not in dates):
                dates.append(sorted_all_dates[i])
                sentiments.append(-1)

    print(sorted_all_dates)
    print(pos_time)
    print(neg_time)
    print(all_sorted)
    print(dates)
    print(sentiments)


    return ({"sentiment": sentiments, "dates": dates, "totaltweets": len(tweet_array)})
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))