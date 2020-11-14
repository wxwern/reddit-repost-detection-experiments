#!/usr/bin/env python3

from enum import Enum
from PIL import Image, UnidentifiedImageError
import imagehash
import math

class Hasher:
    """
    Custom wrapper class to handle hashing of images or text.

    Utilises https://pypi.org/project/ImageHash/ for image hashing.
    """
    def __init__(self):
        pass


    class Type(Enum):
        """An enum representing the hash type"""
        TEXT = 'TEXT'
        IMAGE = 'IMAGE'
        IMAGERGB = 'IMAGERGB'
        def isImage(self):
            return self in (Hasher.Type.IMAGE, Hasher.Type.IMAGERGB)
        def isText(self):
            return self in (Hasher.Type.TEXT,)

    class ImageHashMethod(Enum):
        """An enum representing the method to hash an image"""
        AHASH = 'aHash'
        PHASH = 'pHash'
        DHASH = 'dHash'
        WHASH = 'wHash'

    @staticmethod
    def hash(obj, hashType: str = None, hashMethod: str = None):
        """
        Hashes the image or text using the hasing method.
        An image defaults to the IMAGE type, and string defaults to the TEXT type.

        Parameters:
        - obj: the object to hash.
        - hashType: the type of hash via the Hasher.Type enum or its raw value.
        - hashMethod: the method of hashing via the relevant enum or its raw value.
        """

        if hashType is None:
            if isinstance(obj, str):
                if obj.split('.')[-1].lower() in ('jpg','jpeg','png','gif'):
                    try:
                        obj = Image.open(obj)
                        hashType = Hasher.Type.IMAGE
                    except (FileNotFoundError, UnidentifiedImageError):
                        hashType = Hasher.Type.TEXT
                else:
                    hashType = Hasher.Type.TEXT
            if isinstance(obj, Image):
                hashType = Hasher.Type.IMAGE

        if hashType is None:
            raise ValueError('hashType is not provided')

        if hashMethod is not None:
            if hashType.isText():
                return Hasher.hashText(obj,
                                       hashMethod=hashMethod)
            if hashType.isImage():
                return Hasher.hashImage(obj,
                                        hashMethod=hashMethod,
                                        retainRGB=(hashType==Hasher.Type.IMAGERGB))
        else:
            if hashType.isText():
                return Hasher.hashText(obj)
            if hashType.isImage():
                return Hasher.hashImage(obj,
                                        retainRGB=(hashType==Hasher.Type.IMAGERGB))

    @staticmethod
    def hashImage(image: Image, hashMethod: str = 'dHash', hash_size: int = 8, retainRGB = False):
        """
        Hashes the image given into using the relevant hashing method.

        Parameters:
        - image: accepts a filename or PIL image.
        - hashMethod: accepts a hash method in the ImageHashMethod enum, i.e. aHash, pHash, dHash, wHash.
        - retainRGB: splits and retains separate RGB information in the hash. Will contain three times as much data.
        """
        if isinstance(image, str):
            image = Image.open(image)

        result = {
            Hasher.ImageHashMethod.AHASH.value: imagehash.average_hash,
            Hasher.ImageHashMethod.PHASH.value: imagehash.phash,
            Hasher.ImageHashMethod.DHASH.value: imagehash.dhash,
            Hasher.ImageHashMethod.WHASH.value: imagehash.whash,
        }[hashMethod.value \
          if isinstance(hashMethod, Hasher.ImageHashMethod) else \
          hashMethod] \
        (image, hash_size=hash_size)

        return str(result)

    @staticmethod
    def hashText(text: str, hashMethod: str = 'ENdist'):
        d = {}
        cList = []
        charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
        for c in text.lower():
            if c not in d:
                d[c] = 0
            d[c] += 1
        for c in charset:
            if c not in d:
                d[c] = 0
        maxVal = max(v for k,v in d.items())
        hexadec = ''
        for c in charset:
            v = 0 if maxVal == 0 else min(15, d[c]*16//maxVal)
            hexadec += hex(v)[2:]
        return hexadec

    @staticmethod
    def sim(hash1: str, hash2: str, hashType: str):
        """
        Computes the similarity between two hash strings for a specific hash type.

        Parameters:
        - hash1: first hash string to be compared.
        - hash2: second hash string to be compared.
        - hashType: the type of the hash, i.e. IMAGE or TEXT.
        """
        x = diff(hash1, hash2, hashType)
        if x:
            return 1-x

    @staticmethod
    def diff(hash1: str, hash2: str, hashType: str):
        """
        Computes the difference between two hash strings for a specific hash type.

        Parameters:
        - hash1: first hash string to be compared.
        - hash2: second hash string to be compared.
        - hashType: the type of the hash, i.e. IMAGE or TEXT.
        """

        if hashType in (Hasher.Type.IMAGE.value, Hasher.Type.IMAGE):
            if len(hash1) != len(hash2):
                return 1.0
            l = len(hash1)

            #image hash
            hash1 = imagehash.hex_to_hash(hash1)
            hash2 = imagehash.hex_to_hash(hash2)

            return abs(hash1-hash2)/(l*4)
        elif hashType in (Hasher.Type.TEXT.value, Hasher.Type.TEXT):
            #text hash
            maxCount = 0
            for c in hash1 + hash2:
                maxCount += int(c,16)
            diff = 0
            for i in range(len(hash1)):
                diff += abs(int(hash1[i],16) - int(hash2[i],16))

            if maxCount == 0:
                return 0

            return diff/maxCount
        else:
            raise ValueError('An unexpected hash type ' + str(hashType) + ' was given to compute the hash difference')

