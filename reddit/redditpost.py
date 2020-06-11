#!/usr/bin/env python3

from io import BytesIO
from PIL import Image
from subreddit import Subreddit
from redditor import Redditor
from redditobject import RedditObject

class RedditPost(RedditObject):
    """Abstract representation of a single reddit post"""

    __init_key = object()
    def __init__(self, init_key, subreddit: Subreddit, post_id: str, post_slug: str):
        assert(init_key == self.__class__.__init_key), \
            "You must not initialise " + self.__class__.__name__ + " directly. Please use the .get method instead."
        super().__init__()
        self.__subreddit = subreddit
        self.__id = post_id
        self.__slug = post_slug
        self.__post_title = None
        self.__post_image_url = None
        self.__post_image = None
        self.__author = None
        self.__score = None
        self.__comments = []

    __posts_dict = {}
    @classmethod
    def get(cls, subreddit: Subreddit, post_id: str, post_slug: str = None):
        if post_id in cls.__posts_dict:
            return cls.__posts_dict[post_id]
        new_obj = cls(cls.__init_key, subreddit, post_id, post_slug)
        cls.__posts_dict[post_id] = new_obj
        return new_obj

    #Init
    @classmethod
    def fromUrl(cls, url: str):
        """Creates and returns a reddit post object from a url."""

        url = url.replace('www.reddit.com', '').replace('reddit.com', '').replace('https://','').replace('http://','')
        parts = url.split('/') # [<>, 'r', name, 'comments', post_id, name, <>]

        if parts[1] != 'r' or parts[3] != 'comments':
            raise RedditPost.MalformedUrlError('the url given (' + url + ') is not a valid reddit post url.')

        return RedditPost.get(Subreddit.get(parts[2]), parts[4], parts[5])

    @classmethod
    def fromJson(cls, jsonInput):
        """Creates a RedditPost object from raw JSON input"""
        post_id = jsonInput[0]['data']['children'][0]['data']['id'] if isinstance(jsonInput, list) else jsonInput['data']['id']
        post = RedditPost.get(None, post_id, None)
        post._process(jsonInput)
        return post

    def _process(self, jsonObject):
        postJson = jsonObject[0]['data']['children'][0] if isinstance(jsonObject, list) else jsonObject
        self.__subreddit = Subreddit.get(postJson['data']['subreddit'])
        self.__id = postJson['data']['id']
        self.__slug = postJson['data']['permalink'].split('/')[5]
        self.__post_title = postJson['data']['title']
        self.__author = Redditor.get(postJson['data']['author'])
        self.__score = postJson['data']['score']

        try:
            self.__comments = []
            for commentJson in jsonObject[1]['data']['children']:
                self.__comments.append(RedditComment.fromJson(commentJson))
        except:
            pass

        try:
            if postJson['data']['post_hint'] == 'image':
                self.__post_image_url = postJson['data']['url']
        except:
            pass

    def retrieve(self):
        """Retrieves the data within this comment and saves it to self"""
        self._retrieve(self.getUrl() + '.json')


    #Getters
    def getSubreddit(self) -> Subreddit:
        """Returns the subreddit this post belongs to."""
        return self.__subreddit

    def getId(self) -> str:
        """Returns the id of the post."""
        return self.__id

    def getUrl(self) -> str:
        """Returns the permalink for the post."""
        u = self.getSubreddit().getUrl() + '/comments/' + self.__id + '/'
        if self.__slug:
            u += self.__slug + '/'
        return u

    def getTitle(self) -> str:
        """Returns the title of the post. May be None if not yet retrieved."""
        return self.__post_title

    def getImageUrl(self) -> str:
        """Returns the url of the image post if it has one, otherwise None."""
        return self.__post_image_url

    def getImage(self) -> Image:
        """Returns the image as a PIL Image object, if available, and synchronously from the web if necessary, otherwise None"""
        try :
            if not self.__post_image and self.getImageUrl():
                data = self.__class__.retrieveRawData(self.getImageUrl())
                self.__post_image = Image.open(BytesIO(data.content))

            if self.__post_image:
                return self.__post_image
        except:
            pass
        return None

    def unloadImage(self):
        """Removes the image from memory if present. It'll be redownloaded if getImage is called again."""
        self.__post_image = None

    def getAuthor(self) -> Redditor:
        """Returns the author of the comment. It may be None if not yet retrieved."""
        return self.__author

    def getScore(self) -> int:
        """Returns the score of the comment (upvotes - downvotes). It may be None if not yet retrieved."""
        return self.__score

    def getComments(self) -> list:
        return self.__comments



    def __repr__(self):
        s = '[RedditPost ' + self.__id + ' <' + str(hex(id(self))) + '>'
        a = self.getAuthor()
        t = self.getTitle().replace('\n', '') if self.getTitle() else ''
        if a:
            s += ' by ' + a.getFormattedUsername()
        if t:
            s += ': ' + t[:15] + ('...' if len(t) > 15 else '')
        s += ']'
        return s





class RedditComment(RedditObject):
    """Abstract representation of a single reddit comment"""

    __init_key = object()
    def __init__(self, init_key, reddit_post: RedditPost, comment_id: str):
        assert(init_key == self.__class__.__init_key), \
            "You must not initialise " + self.__class__.__name__ + " directly. Please use the .get method instead."
        super().__init__()
        self.__post = reddit_post
        self.__id = comment_id
        self.__author = None
        self.__comment_text = None
        self.__score = None

    __comments_dict = {}
    @classmethod
    def get(cls, post: RedditPost, comment_id: str):
        if comment_id in cls.__comments_dict:
            return cls.__comments_dict[comment_id]
        new_obj = cls(cls.__init_key, post, comment_id)
        cls.__comments_dict[comment_id] = new_obj
        return new_obj

    #Init
    @classmethod
    def fromUrl(cls, url: str):
        """Creates and returns a reddit post object from a url."""

        url = url.replace('www.reddit.com', '').replace('reddit.com', '').replace('https://','').replace('http://','')
        parts = url.split('/') # [<>, 'r', name, 'comments', post_id, name, comment_id]

        if parts[1] != 'r' or parts[3] != 'comments' or not parts[6]:
            raise RedditComment.MalformedUrlError('the url given (' + url + ') is not a valid reddit post url.')

        comment = RedditComment.get( \
            RedditPost.get(Subreddit.get(parts[2]), parts[4], parts[5]), \
            parts[6] \
        )
        return comment

    @classmethod
    def fromJson(cls, jsonInput):
        """Creates a RedditComment object from raw JSON input."""
        comment = cls.get(None, jsonInput['data']['id'])
        comment._process(jsonInput)
        return comment

    def _process(self, jsonObject):
        url = jsonObject['data']['permalink']
        self.__post = RedditPost.fromUrl(url)
        self.__id = jsonObject['data']['id']
        self.__author = Redditor.get(jsonObject['data']['author'])
        self.__comment_text = jsonObject['data']['body']
        self.__score = jsonObject['data']['score']

    def retrieve(self):
        """Retrieves the data within this comment and saves it to self."""
        self._retrieve(self.getUrl() + '.json')


    #Getters
    def getUrl(self) -> str:
        """Returns the url for a particular comment."""
        return self.__post.getUrl() + self.__id

    def getId(self) -> str:
        """Returns the id of the comment."""
        return self.__id

    def getPost(self) -> RedditPost:
        """Returns the parent post of the comment."""
        return self.__post

    def getText(self) -> str:
        """Returns the plain text contents of the comment. It may be None if not yet retrieved."""
        return self.__comment_text

    def getAuthor(self) -> Redditor:
        """Returns the author of the comment. It may be None if not yet retrieved."""
        return self.__author

    def getScore(self) -> int:
        """Returns the score of the comment (upvotes - downvotes). It may be None if not yet retrieved."""
        return self.__score



    def __repr__(self):
        s = '[RedditComment ' + self.__id + ' <' + str(hex(id(self))) + '>'
        a = self.getAuthor()
        t = self.getText().replace('\n', '') if self.getText() else ''
        if a:
            s += ' by ' + a.getFormattedUsername()
        if t:
            s += ': ' + t[:15] + ('...' if len(t) > 15 else '')
        s += ']'
        return s
