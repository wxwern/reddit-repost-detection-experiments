#!/usr/bin/env python3

try:
    from redditobject import RedditObject
except ImportError:
    from reddit.redditobject import RedditObject

class Subreddit(RedditObject):
    """Abstract representation of a single subreddit"""

    __init_key = object()
    def __init__(self, init_key, name: str):
        assert(init_key == self.__class__.__init_key), \
            "You must not initialise " + self.__class__.__name__ + " directly. Please use the .get method instead."
        super().__init__()
        self.__name = name
        self.__posts = set()

    __subreddit_dict = {}
    @classmethod
    def get(cls, name: str):
        if name in cls.__subreddit_dict:
            return cls.__subreddit_dict[name]
        new_obj = cls(cls.__init_key, name)
        cls.__subreddit_dict[name] = new_obj
        return new_obj

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
        if sort not in ['top', 'hot', 'new', 'controversal', 'rising']:
            print('warning: unsupported post sort method, defaulting to sorting by top')
            sort = 'top'
        return self.getUrl() + '/' + sort + '/'

    def getSearchUrl(self, flair: str, json: bool = False, sort: str = 'top', max_no: int = 100) -> str:
        jsonExt = '.json' if json else ''
        u = self.getUrl() + '/search' + jsonExt + '?restrict_sr=on&t=all&limit=' + str(max_no) + '&sort=' + str(sort) + '&q=flair:"' + flair + '"'
        return u

    def _process(self, jsonObject):
        items = jsonObject['data']['children']
        if items:
            if items[0]['kind'] == 't3': #posts
                try:
                    from redditpost import RedditPost
                except ImportError:
                    from reddit.redditpost import RedditPost
                for item in items:
                    self.__posts.add(RedditPost.fromJson(item))

    def retrieve(self):
        """Retrieves the posts in this subreddit and saves it to self."""
        self.__class__._retrieveList(
            [self],
            [self.getPostsUrl() + '.json?limit=100']
        )

    def retrievePosts(self, sort: str = 'top', flair: str = None, max_no: int = 100):
        """Retrieves the posts in this subreddit with custom sorting or flair filtering and saves it to self."""
        if flair:
            u = self.getSearchUrl(json=True, sort=sort, flair=flair, max_no=max_no)
        else:
            u = self.getPostsUrl() + '.json?limit=' + str(max_no)
        self._retrieve(u)

    def getPosts(self):
        """Returns the posts retrieved from this subreddit."""
        return list(self.__posts)

    def __repr__(self):
        return '[Subreddit ' + self.getFormattedName() + ' <' + str(hex(id(self))) + '>]'
