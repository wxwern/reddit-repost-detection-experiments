#!/usr/bin/env python3

import json
import requests

from subreddit import Subreddit
from redditor import Redditor
from redditpost import RedditPost

class RedditScraper:
    def __init__(self):
        pass

if __name__ == "__main__":

    # testing area
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Connection': 'close',
    }

    print("latest repostsleuthbot comment info")
    p1 = Redditor('repostsleuthbot').getCommentsUrl() + '.json'
    r1 = requests.get(p1, headers)
    data = r1.json()
    if 'data' in data:
        latestComment = data['data']['children'][0]
        print(json.dumps(latestComment, indent=4, sort_keys=True))
    else:
        print(data)

    print("top programmerhumor post info")
    p2 = Subreddit('programmerhumor').getPostsUrl('top') + '.json'
    r2 = requests.get(p2, headers)
    data = r2.json()
    if 'data' in data:
        topPost = data['data']['children'][0]
        print(json.dumps(latestComment, indent=4, sort_keys=True))
    else:
        topPost = {}
        print(data)

    if 'permalink' in topPost:
        print("top comment from top post")
        p3 = RedditPost(topPost['permalink']).getUrl() + '.json'
        r3 = requests.get(p3, headers)
        data = r2.json()
        topComment = data[1]['data']['children'][0]
        print(json.dumps(topComment, indent=4, sort_keys=True))
