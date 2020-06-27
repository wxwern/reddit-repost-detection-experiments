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

import os
if __name__ == "__main__":
    directory = "scraper_cache"
    if not os.path.exists(directory):
        os.makedirs(directory)
    create_filepath = lambda x: directory + "/" + x

    s = Subreddit.get('memes')
    print('retrieving subreddit posts')
    s.retrievePosts()
    while len(s.getPosts()) < 100 and s.hasSubsequentPages():
        print('retrieving additional posts...')
        s.retrievePosts(max_no=5, use_next=True)

    posts = s.getPosts()
    try:
        for i, p in enumerate(posts):
            print('downloading image from post %d of %d' % (i + 1, len(posts)))
            ext = p.getImageUrl().split('/')[-1].split('.')[-1]
            path = create_filepath(s.getName() + '_' + p.getId() + '.' + ext)
            if not os.path.exists(path):
                img = p.getImage()
                if img:
                    img.save(path)
                    print('saved image')
                p.unloadImage()
            else:
                print('image already downloaded')
    except KeyboardInterrupt:
        pass
