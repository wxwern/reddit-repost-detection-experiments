from PIL import Image
from PIL import ImageOps
import pytesseract

class TestOCR:

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



def testImage(name):
    ocr = TestOCR
    image = Image.open(name)
    image.show()
    print(ocr.read(image))
    grayscale = ImageOps.grayscale(image)
    grayscale.show()
    print(ocr.read(grayscale))
    
