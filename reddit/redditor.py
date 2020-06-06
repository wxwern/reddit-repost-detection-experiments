#!/usr/bin/env python3

class Redditor:
    """Abstract representation of a single redditor"""

    def __init__(self, username: str):
        self.__username = username

    def getUsername(self) -> str:
        return self.__username

    def getFormattedUsername(self) -> str:
        """Returns the subreddit prefixed with u/, reddit's standard notation"""
        return 'u/' + self.__username

    def getUrl(self) -> str:
        """Returns the full url of the user"""
        return 'https://www.reddit.com/user/' + self.__username

    def getCommentsUrl(self) -> str:
        """Returns the full url to access the user's comment history."""
        return self.getUrl() + '/comments/'

    def getPostsUrl(self) -> str:
        """Returns the full url to access the user's post history."""
        return self.getUrl() + '/posts/'
