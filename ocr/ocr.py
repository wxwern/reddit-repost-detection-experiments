#!/usr/bin/env python3

from PIL import Image
import pytesseract

class OCR:

    def __init__(self):
        pass

    def read(meme):
        rawtext = pytesseract.image_to_string(meme)
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
