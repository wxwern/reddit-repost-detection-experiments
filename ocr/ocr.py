#!/usr/bin/env python3

from PIL import Image
import pytesseract

class OCR:

    def __init__(self):
        pass

    def read(meme):
        '''pytesseract reads unedited image.
        returned string has no newlines and has one space between all words.
        dashes followed by newlines are removed and the word is merged properly.'''
        rawtext = pytesseract.image_to_string(meme)
        rawtext = rawtext.replace("-\n", "")
        nlsplit = rawtext.split("\n")
        final = ""
        for i in nlsplit:
            edit = i.split(" ")
            newstring = ""
            for g in edit:
                if g != "":
                    newstring = newstring + g + " "
            final = final + newstring
            
        
        return final

    
    pass

ocr = OCR
print(ocr.read("potato.jpg"))
