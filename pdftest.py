import img2pdf
import os, sys

def hasPdf(imageList):
    for imageFile in imageList:
        if (imageFile.endswith("pdf")):
                return True
    return False

def isSequential(imageList):
    currentFile = imageList[0]
    count = 0
    while (currentFile.endswith("jpg") == False and (count < len(imageList))):
        currentFile = imageList[count]
        count += 1
    if (currentFile.endswith("jpg") == False):
        return False
    firstFileCommon = currentFile.split("-")
    if (len(firstFileCommon) == 1):
        return False
    toMatch = firstFileCommon[0]
    isSequential = False
    for imageFile in imageList:
        if imageFile.endswith("jpg"):
            if (toMatch not in imageFile) or ("f" not in imageFile):
                return False
    return True


rootDir = sys.argv[1]
dontProcess = []
for dirName, subdirList, fileList in os.walk(rootDir):
    parent = dirName[0:dirName.rfind("/")]
    parentPath = parent[parent.rfind("/") + 1:]
#    if ("seq.txt" in fileList or "random.txt" in fileList):
#        pdfFile = None
#        for eachFile in fileList:
#            if (eachFile.endswith("pdf")):
#                pdfFile = dirName + "/" + eachFile
#        if (pdfFile):
#            os.remove(pdfFile)
#            print("removed : " + pdfFile)
    if ("seq.txt" in fileList):
        pdfName = parentPath.strip() + ".pdf"
        print("sequential pdf : " + pdfName)
        allImages = []
        print(allImages)
        print(dirName)
        for imageFile in fileList:
            if (imageFile.endswith("jpg") || imageFile.endswith("JPG")):
                allImages.append(dirName + "/" + imageFile)
        if (len(allImages) > 0):
            with open(dirName + "/" + pdfName, "wb") as pdfOutput:
                pdfOutput.write(img2pdf.convert(allImages))
    elif ("random.txt" in fileList):
        print("non sequential directory : " + dirName)
        for imageFile in fileList:
            if imageFile.endswith("jpg") || imageFile.endswith("JPG"):
                pdfName = imageFile.split(".")[0] + ".pdf"
                with open(dirName + "/" + pdfName, "wb") as pdfOutput:
                    pdfOutput.write(img2pdf.convert(dirName + "/" + imageFile))
