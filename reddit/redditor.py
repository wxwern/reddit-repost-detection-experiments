#!/usr/bin/env python3

try:
    from redditobject import RedditObject
except ImportError:
    from reddit.redditobject import RedditObject

class Redditor(RedditObject):
    """Abstract representation of a single redditor"""

    __init_key = object()
    def __init__(self, init_key, username: str):
        assert(init_key == self.__class__.__init_key), \
            "You must not initialise " + self.__class__.__name__ + " directly. Please use the .get method instead."
        super().__init__()
        self.__username = username
        self.__posts = []
        self.__comments = []

    __redditor_dict = {}
    @classmethod
    def get(cls, name: str):
        if name in cls.__redditor_dict:
            return cls.__redditor_dict[name]
        new_obj = cls(cls.__init_key, name)
        cls.__redditor_dict[name] = new_obj
        return new_obj

    def getUsername(self) -> str:
        return self.__username

    def getFormattedUsername(self) -> str:
        """Returns the user prefixed with u/, reddit's standard notation"""
        return 'u/' + self.__username

    def getUrl(self) -> str:
        """Returns the full url of the user"""
        return 'https://www.reddit.com/user/' + self.__username

    def getCommentsUrl(self) -> str:
        """Returns the full url to access the user's comment history."""
        return self.getUrl() + '/comments/'

    def getPostsUrl(self) -> str:
        """Returns the full url to access the user's post history."""
        return self.getUrl() + '/submitted/'

    def _process(self, jsonObject):
        items = jsonObject['data']['children']
        if items:
            if items[0]['kind'] == 't1': #comments
                try:
                    from redditpost import RedditComment
                except ImportError:
                    from reddit.redditpost import RedditComment
                self.__comments = []
                for item in items:
                    self.__comments.append(RedditComment.fromJson(item))
            elif items[0]['kind'] == 't3': #posts
                try:
                    from redditpost import RedditPost
                except ImportError:
                    from reddit.redditpost import RedditPost
                self.__posts = []
                for item in items:
                    self.__posts.append(RedditPost.fromJson(item))

    def retrieve(self):
        """Retrieves comments by this redditor and saves it to self."""
        self.__class__._retrieveList(
            [self, self],
            [self.getCommentsUrl() + '.json?limit=100', self.getPostsUrl() + '.json?limit=25']
        )

    def getComments(self):
        return self.__comments

    def getPosts(self):
        return self.__posts

    def __repr__(self):
        return '[Redditor ' + self.getFormattedUsername() + ' <' + str(hex(id(self))) + '>]'
