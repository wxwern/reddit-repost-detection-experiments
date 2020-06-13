#!/usr/bin/env python3
try:
    from subreddit import Subreddit
    from redditor import Redditor
    from redditpost import RedditPost, RedditComment
    from redditobject import RedditObject
except ImportError:
    from .subreddit import Subreddit
    from .redditor import Redditor
    from .redditpost import RedditPost, RedditComment
    from .redditobject import RedditObject
