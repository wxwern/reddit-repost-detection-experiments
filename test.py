#!/usr/bin/env python3

import random
from reddit import Subreddit, RedditPost
from ocr import OCR

def test_random_memes_post():
    print("this test script is for testing reddit object functionalities and ocr")
    print("|| loading hot posts in r/memes")
    s1 = Subreddit.get('memes')
    s1.retrievePosts(sort='hot')
    print("--> " + str(s1))
    print("\n|| retrieving random post")
    p1 = random.choice(s1.getPosts())
    p1.retrieve()
    print("--> " + str(p1))
    print("--> Title            : " + str(p1.getTitle()))
    print("--> Image URL        : " + str(p1.getImageUrl()))
    print("--> Image Object     : " + str(p1.getImage()))
    if p1.getImage():
        print("\n  +++ Image OCR Text    +++ \n" + OCR.read(p1.getImage().convert('RGB')).strip())
        print("\n\n\n  +++ Image Human Trscb +++ \n" + str(p1.getImageHumanTranscription()))
        print("\n\n\n  +++\n")
    print("\n|| retrieving random comment")
    c1 = random.choice(p1.getComments())
    print("--> " + str(c1))
    print("--> Text      : " + c1.getText())
    return (s1, p1, c1)

def test_random_transcribed_image_post():
    print("|| loading transcribed posts in r/transcribersofreddit")
    s2 = Subreddit.get('transcribersofreddit')
    s2.retrievePosts(sort='new', flair='Completed!')
    print('--> ' + str(s2))
    print('\n|| retrieving random transcribed post')
    p2 = RedditPost.fromUrl(random.choice(s2.getPosts()).getCrosspostUrl())
    p2.retrieve()
    print("--> Title            : " + str(p2.getTitle()))
    print("--> Image URL        : " + str(p2.getImageUrl()))
    print("--> Image Object     : " + str(p2.getImage()))
    if p2.getImage():
        print("\n  +++ Image OCR Text    +++ \n" + OCR.read(p2.getImage().convert('RGB')).strip())
        print("\n\n\n  +++ Image Human Trscb +++ \n" + str(p2.getImageHumanTranscription()))
        print("\n\n\n  +++\n")
    return (s2, p2)

if __name__ == '__main__':
    print('-'*30)
    test_random_memes_post()
    print('-'*30)
    test_random_transcribed_image_post()
    print('-'*30)
