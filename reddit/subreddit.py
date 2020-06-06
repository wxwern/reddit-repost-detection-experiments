#!/usr/bin/env python3

class Subreddit:
    """Abstract representation of a single subreddit"""

    def __init__(self, name: str):
        self.__name = name

    def getName(self) -> str:
        return self.__name

    def getFormattedName(self) -> str:
        """Returns the subreddit prefixed with r/, reddit's standard notation"""
        return 'r/' + self.__name

    def getUrl(self) -> str:
        """Returns the full url of the subreddit"""
        return 'https://www.reddit.com/r/' + self.__name

    def getPostsUrl(self, sort: str = 'top') -> str:
        """Returns the url to retrieve recent posts via sort method (defaults to top)"""
        if sort not in ['top', 'hot', 'new', 'controversal']:
            print('warning: unsupported post sort method, defaulting to sorting by top')
            sort = 'top'
        return self.getUrl() + '/' + sort + '/'
