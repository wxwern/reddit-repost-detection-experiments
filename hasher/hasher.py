#!/usr/bin/env python3

from enum import Enum
from PIL import Image, UnidentifiedImageError
import imagehash

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
    def hashImage(image: Image, hashMethod: str = 'dHash', retainRGB: bool = False):
        """
        Hashes the image given into using the relevant hashing method.

        Parameters:
        - image: accepts a filename or PIL image.
        - hashMethod: accepts a hash method in the ImageHashMethod enum, i.e. aHash, pHash, dHash, wHash.
        - retainRGB: splits and retains separate RGB information in the hash. Will contain three times as much data.
        """
        if isinstance(image, str):
            image = Image.open(image)

        if retainRGB:
            #TODO: implement RGB information retention
            raise NotImplementedError('Retain RGB information within a hash is not implemented yet')

        result = {
            Hasher.ImageHashMethod.AHASH.value: imagehash.average_hash,
            Hasher.ImageHashMethod.PHASH.value: imagehash.phash,
            Hasher.ImageHashMethod.DHASH.value: imagehash.dhash,
            Hasher.ImageHashMethod.WHASH.value: imagehash.whash,
        }[hashMethod.value \
          if isinstance(hashMethod, Hasher.ImageHashMethod) else \
          hashMethod] \
        (image)

        return str(result)

    @staticmethod
    def hashText(text: str, hashMethod: str = None):
        #TODO: Implement text hashing
        raise NotImplementedError('Text hashing is not yet implemented')

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
            #image hash
            hash1 = imagehash.hex_to_hash(hash1)
            hash2 = imagehash.hex_to_hash(hash2)
        elif hashType in (Hasher.Type.TEXT.value, Hasher.Type.TEXT):
            #text hash
            #TODO: Implement text hashing
            raise NotImplementedError('Text hashing is not yet implemented')
        else:
            raise ValueError('An unexpected hash type ' + str(hashType) + ' was given to compute the hash difference')

        return abs(hash1-hash2)
