#!/usr/bin/env python3

import json
import requests

class RedditObject:
    """The base class for all reddit objects."""

    headers = {
        'User-Agent': 'python:GeneralRepostiRedditScraper:v0.9 (by /u/no_comments_no_posts)',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Connection': 'close',
    }
    def __init__(self):
        self.headers = self.__class__.headers

    class MalformedUrlError(Exception):
        """A representation of an error caused by an invalid url input"""

    class InvalidResponseError(Exception):
        """A representation of an error caused by an invalid response from reddit"""
        def __init__(self, message: str, code: int):
            super().__init__(message)
            self.code = code

        def __str__(self):
            return '[' + str(self.code) + '] ' + super.__str__()


    def _retrieveRawResponse(self, url: str):
        """Retrieves the raw response provided by reddit with the given url via a standard request."""
        try:
            res = requests.get(url, headers=self.headers)
            res = res.json()
        except requests.exceptions.RequestException as e:
            raise self.__class__.InvalidResponseError(str(e), -2)

        if not res or 'data' not in res:
            if 'code' in res and 'message' in res:
                raise self.__class__.InvalidResponseError(res['message'], res['code'])
            if res:
                raise self.__class__.InvalidResponseError(json.dumps(res), -1)
            raise self.__class__.InvalidResponseError('An invalid response was received', -1)

        return res

    @staticmethod
    def _retrieveRawResponses(objects: list, urlList: list) -> list:
        """Retrieves the raw responses provided by reddit via the given objects using standard requests, and returns the objects list."""
        tmpType = None
        for x in objects:
            if not tmpType:
                tmpType = x.__class__
            elif tmpType != x.__class__:
                raise ValueError('Not all objects provided in the objects list are of the same type.')

        #TODO: Implement bulk retrieval
        return [tmpType._retrieveRawResponse(u) for u in urlList]

    def _process(self, jsonObject):
        """Processes the given json object and embed it into self."""
        raise NotImplementedError()

    @staticmethod
    def _processList(objects: list, jsonObjects: list):
        """Processes a list of json objects and embed their information into their respective objects"""
        for i, x in enumerate(jsonObjects):
            objects[i]._process(x)
        return objects

    def _retrieve(self, url: str):
        """Retrieves the response provided by reddit and embed it on self."""
        return self._process(self._retrieveRawResponse(url))

    @staticmethod
    def _retrieveList(objects: list, urls: list) -> list:
        """Retrieves the response provided by reddit, and embed them onto the relevant objects. Requires all reddit objects in the list to be of the same type."""

        tmpType = None
        for x in objects:
            if not tmpType:
                tmpType = x.__class__
            elif tmpType != x.__class__:
                raise ValueError('Not all objects provided in the objects list are of the same type.')

        return tmpType._processList(objects, tmpType._retrieveRawResponses(urls))
