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
    def read2(meme):
        rawdata = pytesseract.image_to_data(meme, output_type=pytesseract.Output.DICT)
        groups = OCR.getTextGroups(rawdata)
        groups.sort(key=lambda x: x.getTop())
        return '\n\n'.join(list(map(lambda x: x.getText(), groups)))


    @staticmethod
    def formattedPytesseractImageData(data):
        '''
        Reformats pytesseract.image_to_data dict output into a more reasonable form, i.e. data[idx][param] rather than the weird data[param][idx] format.

        You can use this method redundantly even on already formatted data. This is because if it detects the input parameter to be already in the data[idx][param] format, it'll exit returning its input as output.
        '''

        if isinstance(data, list):
            if len(data) == 0 or isinstance(data[0], dict):
                return data

        if isinstance(data, dict):
            output = [None] * len(data.get('text'))
            for key, value in data.items():
                for i, e in enumerate(value):
                    if output[i] is None:
                        output[i] = {}
                    output[i][key] = e
            return list(filter(lambda x: x['text'].strip() != '', output))

        raise ValueError('Are you sure the correct pytesseract input is provided? Expecting a dict but got %s' % str(type(data)))

    class TextGroup:

        def __init__(self, top: int, left: int, width: int, height: int, text: str = None):

            super().__init__()

            self.__top = top
            self.__left = left
            self.__width = width
            self.__height = height
            self.__wordlist = [text]

        def newWord(self, data: dict):

            if isinstance(data, dict):

                oritop = self.__top
                orileft = self.__left
                oriheight = self.__height
                oriwidth = self.__width

                self.__top = min(oritop, data.get("top"))
                self.__left = min(orileft, data.get("left"))
                self.__height = max(oritop + oriheight, data.get("top") + data.get("height")) - self.__top
                self.__width = max(orileft + oriwidth, data.get("left") + data.get("width")) - self.__left
                self.__wordlist.append(data.get("text"))

            elif isinstance(data, str):
                self.__wordlist.append(data)

            else:
                raise ValueError('The given word is not in any accepted format!')


        def getTop(self) -> int:
            return self.__top

        def getLeft(self) -> int:
            return self.__left

        def getWidth(self) -> int:
            return self.__width

        def getHeight(self) -> int:
            return self.__height

        def getWordList(self) -> list:
            return self.__wordlist

        def getText(self) -> str:
            '''Returns formatted text from the wordlist. Spaces are used to join the words.'''
            return ' '.join(self.getWordList()).replace(' \n ', '\n')

    @staticmethod
    def getTextGroups(wordlist):
        '''Returns a list of TextGroup objects from a formatted word list from the pytesseract.image_to_data method'''


        #we format the wordlist. this should guarantee that the format is valid
        wordlist = OCR.formattedPytesseractImageData(wordlist)

        #Getting an average height for spacing between lines
        wordcount = 0
        totalheight = 0
        for i in wordlist:
            wordcount = wordcount + 1
            totalheight = totalheight + i.get("height")
        #avgheight = totalheight // wordcount

        finalgrouping = []

        #boxes
        for i in wordlist:
            word_height = i.get('height')
            X_FACTOR = 2.0
            Y_FACTOR = 1.5

            #check through all existing groups and see which to add to
            consider = None
            c_x_dist = None
            c_y_dist = None
            c_dist = None

            for group in finalgrouping:
                group_centre = (group.getLeft() + group.getWidth()/2, group.getTop() + group.getHeight()/2)
                i_centre = (i.get("left") + i.get("width")/2, i.get("top") + i.get("height")/2)

                x_dist = abs(group_centre[0] - i_centre[0]) - (group.getWidth()/2 + i.get('width')/2)
                y_dist = abs(group_centre[-1] - i_centre[-1]) - (group.getHeight()/2 + i.get('height')/2)
                dist = abs(x_dist - word_height*X_FACTOR) + \
                       abs(y_dist - word_height*Y_FACTOR)

                if x_dist < word_height * X_FACTOR and \
                    y_dist < word_height * Y_FACTOR:

                    if consider is None or dist < c_dist:
                        consider = group
                        c_x_dist = x_dist
                        c_y_dist = y_dist
                        c_dist = dist

            if consider is None:
                #create a new group since it's not added to any existing group
                finalgrouping.append(OCR.TextGroup(top    = i.get("top"), \
                                                   left   = i.get("left"), \
                                                   width  = i.get("width"), \
                                                   height = i.get("height"), \
                                                   text   = i.get("text")))
            else:
                #if c_y_dist > 0:
                #    consider.newWord('\n')
                consider.newWord(i)

        return finalgrouping


if __name__ == "__main__":
    pass

