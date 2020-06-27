#!/usr/bin/env python3

import json
import requests
import time
import datetime

class RedditObject:
    """The base class for all reddit objects."""

    headers = {
        'User-Agent': 'python:GeneralRepostiRedditScraper:v0.9 (by /u/no_comments_no_posts)',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Connection': 'close',
    }
    def __init__(self):
        self.headers = self.__class__.headers

    class MalformedUrlError(RuntimeError):
        """A representation of an error caused by an invalid url input"""

    class InvalidResponseError(RuntimeError):
        """A representation of an error caused by an invalid response from reddit"""
        def __init__(self, message: str, code: int):
            super().__init__(message)
            self.code = code

        def __str__(self):
            return '[' + str(self.code) + '] ' + super().__str__()


    __last_retrieve_timestamp = 0
    @classmethod
    def retrieveRawData(cls, url: str) -> requests.Request:
        """Retrieves the request and returns a requests.Request object"""

        #request limit to 60 times per minute
        time_delay = max(0, cls.__last_retrieve_timestamp - datetime.datetime.now().timestamp() + 1)
        cls.__last_retrieve_timestamp = datetime.datetime.now().timestamp()

        time.sleep(time_delay)

        #send the request with teh relevant headers
        print(url)
        return requests.get(url, headers=cls.headers)

    def _retrieveRawResponse(self, url: str):
        """Retrieves the raw response provided by reddit with the given url via a standard request."""
        try:
            res = self.__class__.retrieveRawData(url)
            res = res.json()
        except requests.exceptions.RequestException as e:
            raise self.__class__.InvalidResponseError(str(e), -2)
        except json.decoder.JSONDecodeError:
            raise self.__class__.InvalidResponseError(str(e), -3)

        checks = res
        if not isinstance(checks, list):
            checks = [checks]

        for opt in checks:
            if not opt or 'data' not in opt:
                if 'code' in opt and 'message' in opt:
                    raise self.__class__.InvalidResponseError(opt['message'], opt['code'])
                if opt:
                    raise self.__class__.InvalidResponseError(json.dumps(opt), -1)
                raise self.__class__.InvalidResponseError('An invalid response was received', -1)

        return res

    @classmethod
    def _retrieveRawResponses(cls, objects: list, urlList: list) -> list:
        """Retrieves the raw responses provided by reddit via the given objects using standard requests, and returns the objects list."""
        tmpType = None
        for x in objects:
            if not tmpType:
                tmpType = x.__class__
            elif tmpType != x.__class__:
                raise ValueError('Not all objects provided in the objects list are of the same type.')

        #TODO: Implement bulk retrieval
        return [objects[i]._retrieveRawResponse(u) for i, u in enumerate(urlList)]

    def _process(self, jsonObject):
        """Processes the given json object and embed it into self."""
        raise NotImplementedError()

    @classmethod
    def _processList(cls, objects: list, jsonObjects: list):
        """Processes a list of json objects and embed their information into their respective objects"""
        for i, x in enumerate(jsonObjects):
            objects[i]._process(x)
        return objects

    def _retrieve(self, url: str):
        """Retrieves the response provided by reddit and embed it on self."""
        return self._process(self._retrieveRawResponse(url))

    def retrieve(self):
        """Retrieves the contents of the object from reddit. This method should return self to allow for chaining."""
        raise NotImplementedError()

    @classmethod
    def _retrieveList(cls, objects: list, urls: list) -> list:
        """Retrieves the response provided by reddit, and embed them onto the relevant objects. Requires all reddit objects in the list to be of the same type."""

        tmpType = None
        for x in objects:
            if not tmpType:
                tmpType = x.__class__
            elif tmpType != x.__class__:
                raise ValueError('Not all objects provided in the objects list are of the same type.')

        return tmpType._processList(objects, tmpType._retrieveRawResponses(objects, urls))
