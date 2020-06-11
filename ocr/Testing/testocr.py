from PIL import Image
from PIL import ImageOps
import pytesseract

class TestOCR:

    def __init__(self):
        pass

    def read(meme, original: bool):
        '''with added original text feature! :D'''
        rawtext = pytesseract.image_to_string(meme)
        if original:
            return rawtext
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



def testImage(name):
    ocr = TestOCR
    image = Image.open(name)
    grayscale = ImageOps.grayscale(image)
    print("Original:")
    print(ocr.read(image, True))
    print("-----------------------------------")
    print(ocr.read(image, False))
    print("=======================================================")
    print("Grayscale original:")
    print(ocr.read(grayscale, True))
    print("-----------------------------------")
    print(ocr.read(grayscale, False))
    
    
    
