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
        return list(filter(lambda x: x['text'].strip() != '', output))
       
            
    class TextGroup:

        def __init__(self, top: int, left: int, width: int, height: int, text: str):
            
            super().__init__()
            
            self.__top = top
            self.__left = left
            self.__width = width
            self.__height = height
            self.__wordlist = [text]
        
        def newWord(data: dict):
            
            oritop = self.__top
            orileft = self.__left
            oriheight = self.__height
            oriwidth = self.__width
            
            self.__top = min(oritop, data.get("top"))
            self.__left = min(orileft, data.get("left"))
            self.__height = max(oritop + oriheight, data.get("top") + data.get("height")) - self.__top
            self.__width = max(orileft + oriwidth, data.get("left") + data.get("width")) - self.__left
            self.__wordlist.append(data.get("text"))

    def getTextGroups(wordlist):
        finalgrouping = []
        '''Getting an average height for spacing between lines'''
        wordcount = 0
        totalheight = 0
        for i in wordlist:
            wordcount = wordcount + 1
            totalheight = totalheight + i.get("height")
        avgheight = totalheight // wordcount

        '''boxes'''
        for i in wordlist:
            if finalgrouping == []:
                finalgrouping.append(TextGroup(i.get("top"), i.get("left"), i.get("width"), i.get("height"), i.get("text")))
            for group in finalgrouping:
                group_centre = (group.__left + group.__width/2, group.__top + group.__height/2)
                i_centre = (i.get("left") + i.get("width")/2, i.get("top") + i.get("height")/2)

                x_dist = abs(group.centre[0] - i.centre[0]) - (a.width/2 + b.width/2)
                y_dist = abs(group.centre[-1] - i_centre[-1]) - (a.height/2 + b.height/2)

                if x_dist < 0 and y_dist < 0:
                    group.newWord(i)
                else:
                    finalgrouping.append(TextGroup(i.get("top"), i.get("left"), i.get("width"), i.get("height"), i.get("text")))


if __name__ == "__main__":
    pass

