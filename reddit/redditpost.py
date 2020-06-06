#!/usr/bin/env python3

try:
    from subreddit import Subreddit
except ImportError:
    from reddit.subreddit import Subreddit

class RedditPost:
    """Abstract representation of a single reddit post"""

    class Comment:
        """Abstract representation of a single reddit comment"""
        def __init__(self, reddit_post, comment_id: str):
            self.__post = reddit_post
            self.__id = comment_id

        def getUrl(self) -> str:
            """Returns the url for a particular comment"""
            return self.__post.getUrl() + self.__id

        def getPost(self):
            return self.__post

        def getText(self) -> str:
            pass #TODO: Implement comment text retrieval

    class MalformedUrlError(RuntimeError):
        """A representation of an error caused by an invalid url input"""

    def __init__(self, url: str):
        """Creates and returns a reddit post object from a url if its valid, otherwise None."""
        if not url.startswith('https://'):
            raise RedditPost.MalformedUrlError('the url given (' + url + ') is not a valid url.')

        parts = url.split('/')[2:] # [domain, 'r', name, 'comments', post_id, name, comment_id?]

        if (parts[0] != 'www.reddit.com' and parts[0] != 'reddit.com') or parts[1] != 'r' or parts[3] != 'comments':
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
        pass #TODO: Implement comment list retrieval in the form of [Comment()]
