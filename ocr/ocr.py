#!/usr/bin/env python3

from PIL import Image
import pytesseract
import json

class OCR:

    def __init__(self):
        pass

    @staticmethod
    def read(meme, original: bool = False):
        '''Reads the image directly using pytesseract, unedited, and returns the text result.

        By default, returned string has no newlines and has one space between all words.
        Dashes followed by newlines are removed and the word is merged properly.

        To get the raw output, set the original parameter to True.
        '''
        rawtext = pytesseract.image_to_string(meme)
        if original:
            return rawtext
        rawtext = rawtext.replace("-\n", "")
        parasplit = rawtext.split("\n\n")
        final = ""
        for para in parasplit:
            nlsplit = para.strip().split("\n")
            for i in nlsplit:
                edit = i.split(" ")
                newstring = ""
                for g in edit:
                    if g != "":
                        newstring += g + " "
                final += newstring
            final = final.strip() + "\n\n"

        return final.strip()

    @staticmethod
    def formattedPytesseractImageData(data):
        """Reformats pytesseract.image_to_data dict output into a more reasonable form, i.e. data[idx][param] rather than the weird data[param][idx] format"""
        output = [None] * len(data['text'])
        for key, value in data.items():
            for i, e in enumerate(value):
                if output[i] is None:
                    output[i] = {}
                output[i][key] = e
        reference = list(filter(lambda x: x['text'].strip() != '', output))
        paralist = []
        for i in reference:
            if paralist == []:
                paralist.append(i)
            
                
        

if __name__ == "__main__":
    pass

