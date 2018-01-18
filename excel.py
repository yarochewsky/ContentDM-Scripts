# Spreadsheets editing library
# University of Washington Digital Strategies, Winter '18
# Daniel Fonseca Yarochewsky
# This library is a set of tools to edit tab delimited files output by Excel.
import csv, os, collections
from collections import deque

# given the filename with tab-delimited data, stores every value corresponding to a filed name
# in a dictionary
# e.g. collection['Title'] gives all the titles in the data. Returns the created dict.
def mapDataToCollection(fileName):
    data = list(csv.reader(open(fileName, 'rU'), delimiter='\t'))
    fieldNames = data[0]
    collection = collections.OrderedDict()

    # first, populate the keys in the dictionary  (field names)
    for field in fieldNames:
        collection[field] = []

    for num in range (1, len(data)):
        lineOfData = data[num]
        for num2 in range (0, len(lineOfData)):
            eachValueInLineOfData = lineOfData[num2]
            collection.get(fieldNames[num2]).append(eachValueInLineOfData)

    return collection

# given a collection dictionary, generates and returns a list of tab-separated strings
# containing each row of the collection. Note that we're using \r\n as end of line, as per
# the specification of Excel since we're converting xls spreadsheets to tab-delimited txt files,
# and inputting those files to this program. The resulting list is a queue. (FIFO)
def generatePrintableCollection(collection):
    printableCol = deque([])
    row = ''
    colkeys = collection.keys()
    row += colkeys[0]
    for num in range(1, len(colkeys)):
        row += '\t' + colkeys[num]
    row += '\r\n'
    printableCol.append(row)

    normalLen = len(collection[colkeys[0]])

    for rowNumber in range(0, normalLen):
        row = collection[colkeys[0]][rowNumber]
        for colkey in range(1, len(colkeys)):
            eachValue = collection[colkeys[colkey]][rowNumber]
            row += '\t' + eachValue
        if (rowNumber < normalLen): # there's no end of line after file in the original Excel files
            row += '\r\n'
        printableCol.append(row)
    return printableCol

# given a collection, and a field name, creates a new column with that field name,
# and initializes every row of that column to empty string.
def addFieldToCol(collection, fieldName):
    collection[fieldName] = []
    normalLen = len(collection[collection.keys()[0]])
    for num in range(0, normalLen):
        collection[fieldName].append('')

# given a collection, and a filename, writes the collection, line by line, to the
# given file.
def writeCollectionToFile(collection, filename):
    printDict = generatePrintableCollection(col)
    f = open(filename, 'w')
    for num in range (0, len(printDict)):
        f.write(printDict.popleft()) # fifo order
    f.close()

# given a collection, matches and replaces all file types to a standard type
# among : MovingImage, StillImage, Sound, or Text. Sets file type to Text in case
# no file type is found for the collection
def normalizeType(collection):
    typeMatch = {'.gif' : 'StillImage', '.jpg' : 'StillImage', '.tif' : 'StillImage',
                 '.flv' : 'MovingImage', 'html' : 'Text', 'jp2' : 'StillImage',
                 '.m4v' : 'MovingImage', '.mp3' : 'Sound', '.pdf' : 'Text', '.pdfpage' : 'Text',
                 '.psd' : 'MovingImage', '.txt' : 'Text'}

    fileTypeCol = collection['CONTENTdm file name']
    colkeys = collection.keys()
    typeColumnName = 'Type' if 'Type' in colkeys else 'Type-DCMI'
    typeKeys = typeMatch.keys()
    inferedCollectionType = ''
    notStandardized = []
    for num in range(0, len(fileTypeCol)):
        fileType = os.path.splitext(fileTypeCol[num])[1].lower()
        if fileType in typeKeys:
            standardType = typeMatch[fileType]
            collection[typeColumnName][num] = standardType
            inferedCollectionType = standardType if inferedCollectionType == '' else inferedCollectionType
        else:
            if inferedCollectionType != '':
                collection[typeColumnName][num] = inferedCollectionType
            else:
                notStandardized.append(num)

    inferedCollectionType = 'Text' if inferedCollectionType == '' else inferedCollectionType
    for each in notStandardized:
        collection[typeColumnName][each] = inferedCollectionType
