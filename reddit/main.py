#!/usr/bin/env python3

try:
    from subreddit import Subreddit
    from redditor import Redditor
    from redditpost import RedditPost, RedditComment
    from redditobject import RedditObject
except ImportError:
    from reddit.subreddit import Subreddit
    from reddit.redditor import Redditor
    from reddit.redditpost import RedditPost, RedditComment
    from reddit.redditobject import RedditObject

if __name__ == "__main__":
    """For testing purposes"""
    print("\nloading hot posts in r/memes")
    s = Subreddit.get('memes')
    s.retrievePosts(sort='hot')
    print("--> " + str(s))
    print("\nretrieving first post")
    p = s.getPosts()[0]
    p.retrieve()
    print("--> " + str(p))
    print("\n\nshowing top post")
    print("--> " + p.getTitle())
    print("--> " + p.getImageUrl())
    print("--> " + str(p.getImage()))
    print("\nshowing top comment")
    c = p.getComments()[0]
    print("--> " + c.getText())
    print()
