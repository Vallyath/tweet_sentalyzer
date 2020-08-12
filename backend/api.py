from flask import Flask, request
from requests_oauthlib import OAuth1Session
import requests, os, json, base64, pickle, nltk, re, string, calendar, datetime, psutil
from nltk.tokenize import TweetTokenizer
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

process = psutil.Process(os.getpid())
print("Startup ", process.memory_info().rss)

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
print("Making API key ", process.memory_info().rss)

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
    totaltweets = 0
    total_dict = {}
    total_time = {}
    daily_total = {}
    all_dates = []
    all_sorted = {}
    dates = []
    sentiments = []

    print("API Calling ", process.memory_info().rss)

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

    for i in range(30):
        response = requests.get(url, headers=search_headers, params=search_params)
        data = json.loads(response.content)
        for j in range(len(data["statuses"])):
            date = data["statuses"][j]["created_at"][4:11] + data["statuses"][j]["created_at"][26:30]
            tweet = data["statuses"][j]["text"]
            tweet_tokens = removeNoise(tt.tokenize(tweet), stop_words)
            tweet_sentiment = classifier.classify(dict([token, True] for token in tweet_tokens))
            totaltweets += 1
            if(tweet_sentiment == "Positive"):
                if date in total_dict:
                    total_dict[date] += 1
                else:
                    total_dict[date] = 1
            elif(tweet_sentiment == "Negative"):
                if date in total_dict:
                    total_dict[date] -= 1
                else:
                    total_dict[date] = -1
            if date in daily_total:
                daily_total[date] += 1
            else:
                daily_total[date] = 1
            next_results_url_params = data['search_metadata']['next_results']
            next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
            search_params["max_id"] = next_max_id
            search_params["include_entities"] = 'true'
    
    
    print(f"Total Sentiment List: {total_dict}")
    print(f"Daily Total: {daily_total}")

    for key in total_dict:
        total_dict[key] = total_dict[key] / daily_total[key]

    print(f"After daily total calculations: {total_dict}")

    for key in total_dict:
        total_time[f"{months[key[:3]]}-{key[4:6]}-{key[7:11]}"] = total_dict[key]
    print("Sorting dates...")
    total_dates = [datetime.datetime.strptime(key, '%m-%d-%Y') for key in total_time]
    total_dates.sort()
    sorted_all_dates = [datetime.datetime.strftime(dates, '%m-%d-%Y') for dates in total_dates]

    for i in range(len(sorted_all_dates)):
        dates.append(sorted_all_dates[i])
        if(sorted_all_dates[i][1:] in total_time):
            sentiments.append(total_time[sorted_all_dates[i][1:]])
        else:
            sentiments.append(total_time[sorted_all_dates[i]])

    print("Dates ", dates)
    print("Sentiments ", sentiments)

    return ({"sentiment": sentiments, "dates": dates, "totaltweets": totaltweets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
