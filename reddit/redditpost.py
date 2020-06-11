#!/usr/bin/env python3

from subreddit import Subreddit
from redditobject import RedditObject

class RedditPost(RedditObject):
    """Abstract representation of a single reddit post"""

    def __init__(self, url: str):
        """Creates and returns a reddit post object from a url."""
        super().__init__()

        url = url.replace('www.reddit.com', '').replace('reddit.com', '').replace('https://','').replace('http://','')
        parts = url.split('/') # [<>, 'r', name, 'comments', post_id, name, comment_id?]

        if parts[1] != 'r' or parts[3] != 'comments':
            raise RedditPost.MalformedUrlError('the url given (' + url + ') is not a valid reddit post url.')

        subreddit_name = parts[2]
        post_id = parts[4]
        post_urlname = parts[5]

        self.__setup(Subreddit(subreddit_name), post_id, post_urlname)

    def __setup(self, subreddit: Subreddit, post_id: str, post_urlname: str = None):
        """<internal method> setup the current post object with the relevant params."""
        self.__subreddit = subreddit
        self.__id = post_id
        self.__urlname = post_urlname

    def getSubreddit(self) -> Subreddit:
        """Returns the subreddit this post belongs to."""
        return self.__subreddit

    def getId(self) -> str:
        """Returns the id of the post."""
        return self.__id

    def getUrl(self) -> str:
        """Returns the permalink for the post."""
        return self.getSubreddit().getUrl() + '/comments/' + self.__id + '/' + self.__urlname + '/'

    def getComments(self) -> list:
        pass #TODO: Implement comment list retrieval in the form of [RedditComment()]


class RedditComment(RedditObject):
    """Abstract representation of a single reddit comment"""

    def __init__(self, reddit_post: RedditPost, comment_id: str, comment_text: str = None, score: int = 0):
        super().__init__()
        self.__post = reddit_post
        self.__id = comment_id
        self.__comment_text = comment_text
        self.__score = score

    def getUrl(self) -> str:
        """Returns the url for a particular comment"""
        return self.__post.getUrl() + self.__id

    def getPost(self) -> RedditPost:
        return self.__post

    def getText(self) -> str:
        return self.__comment_text

    def getScore(self) -> int:
        return self.__score
