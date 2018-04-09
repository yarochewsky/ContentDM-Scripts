# coding:utf-8
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
# Spreadsheets editing library
# University of Washington Digital Strategies, Winter '18
# Daniel Fonseca Yarochewsky
# This library is a set of tools to edit tab delimited files output by Excel.
import csv, os, collections
from collections import deque
import contentdm_api
import re
from os.path import basename
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree


STANDARD_RESTRICTIONS_STRING = ('For information on permissions for use and reproductions please' +
                                'visit UW Libraries Special Collections Use Permissions page:' +
                                'http://www.lib.washington.edu/specialcollections/services/' +
                                'permission-for-use')
COPYRIGHT_NOT_EVALUATED = 'http://rightsstatements.org/vocab/CNE/1.0/'
IN_COPYRIGHT = 'http://rightsstatements.org/vocab/InC/1.0/'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# print bcolors.FAIL


# given the filename with tab-delimited data, stores every value corresponding to a filed name
# in a dictionary
# e.g. collection['Title'] gives all the titles in the data. Returns the created dict.
def mapDataToCollection(fileName):
    # remember to change delimiter as appropriate; most commonly ',' or '\t'
    data = list(csv.reader(open(fileName, 'rU'), delimiter='\t'))
    # data = list(csv.reader(open(fileName, 'rU'), skipinitialspace=True))
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

# returns a pretty-printed (indented, standard XML) XML string for the given element
def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# creates all .desc files cloning the format of the ContentDm Project Client
# pulling data from the collection's metadata so that the files can be copied
# to the ContentDm Project folder and loaded as original project client files
def reconstructDesc(collection, fieldsMetadata):
    defaultColumnLength = len(collection['Title']) # take length of some arbitrary field
    for number in range(0, defaultColumnLength):
        itemMetadataWrapper = Element('itemmetadata')
        for field in fieldsMetadata:
            fieldName = field['name']
            nickname = field['nick']
            elementChild = SubElement(itemMetadataWrapper, nickname)
            if fieldName in list(collection.keys()):
                elementChild.text = collection[fieldName][number]
        addProjectClientBookeepingTags(itemMetadataWrapper)
        xmlString = prettify(itemMetadataWrapper)
        fileName = collection['CONTENTdm number'][number] + ".desc"
        fullPathFile = os.path.join("loc", fileName)
        root = ElementTree.ElementTree(ElementTree.fromstring(xmlString))
        root.write(fullPathFile, encoding="utf-8", xml_declaration=False,
    	           method="xml", short_empty_elements=False)
        fileContents = []
        with open(fullPathFile, "r") as oldFile:
            fileContents = oldFile.read()
        with open(fullPathFile, "w") as newFile:
            newFile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            newFile.write(fileContents)

# given the xml tree root, adds the tags that always appear at the end
# of each .desc file: dmimage, dmad1, dmad2, dmaccess
def addProjectClientBookeepingTags(root):
    tags = ["dmimage", "dmad1", "dmad2", "dmaccess"]
    for tag in tags:
        elementChild = SubElement(root, tag)

# given a collection dictionary, generates and returns a list of tab-separated strings
# containing each row of the collection. Note that we're using \r\n as end of line, as per
# the specification of Excel since we're converting xls spreadsheets to tab-delimited txt files,
# and inputting those files to this program. The resulting list is a queue. (FIFO)
# REMEMBER to change delimiter as appropriate; most commonly ',' or '\t'
def generatePrintableCollection(collection):
    printableCol = deque([])
    row = ''
    colkeys = list(collection.keys())
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
    normalLen = len(collection[list(collection.keys())[0]])
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
                 '.psd' : 'MovingImage', '.txt' : 'Text', '.mp4' : 'MovingImage'}

    fileTypeCol = collection['CONTENTdm file name']
    colkeys = list(collection.keys())
    typeKeys = list(typeMatch.keys())
    inferedCollectionType = ''
    notStandardized = []
    for num in range(0, len(fileTypeCol)):
        fileType = os.path.splitext(fileTypeCol[num])[1].lower()
        if fileType in typeKeys:
            standardType = typeMatch[fileType]
            collection['Type-DCMI'][num] = standardType
            inferedCollectionType = standardType if inferedCollectionType == '' else inferedCollectionType
        else:
            if inferedCollectionType != '':
                collection['Type-DCMI'][num] = inferedCollectionType
            else:
                notStandardized.append(num)

    inferedCollectionType = 'Text' if inferedCollectionType == '' else inferedCollectionType
    for each in notStandardized:
        collection['Type-DCMI'][each] = inferedCollectionType
    reportField(collection, 'Type-DCMI')

# given a collection, fix the restrictions field, inputting STANDARD_RESTRICTIONS_STRING if
# no restrictions could be inferred from the collection
def fixRestrictions(collection):
    fixPredictableField(collection, 'Restrictions', STANDARD_RESTRICTIONS_STRING)
    reportField(collection, 'Restrictions')

# given a collection and its formal name, fix digital collection field, inputting the collection's
# name if no digital collection string could be inferred from the other items in the collection
def fixDigitalCollection(collection, collectionName):
    fixPredictableField(collection, 'Digital Collection', collectionName)
    reportField(collection, 'Digital Collection')

# given a collection, fieldname and default sting value, fixes
# all rows for that field column with the values inferred from its sibling
# items in the column, or if none is there, places default string in the row
def fixPredictableField(collection, fieldName, defaultValue):
    column = collection[fieldName]
    inferedFieldString = ''
    notThereYet = []
    for num in range(0, len(column)):
        rowInColumn = column[num]
        if rowInColumn != '':
            if inferedFieldString == '':
                inferedFieldString = rowInColumn
        else:
            if inferedFieldString != '':
                column[num] = inferedFieldString
            else:
                notThereYet.append(num)
    for each in notThereYet:
        if inferedFieldString != '':
            column[each] = inferedFieldString
        else:
            column[each] = defaultValue

# given collection, finds standard collection date. Returns -1 if not found
def inferCollectionDate(collection):
    dates = collection['Date-EDTF']
    for num in range(len(dates) - 1, 0, -1):
        if dates[num] != '':
            return dates[num]
    return -1

# finds the earliest date in a date string. Returns a 4-digit date integer or
# -1 if not found or not proper date
def normalizeDate(dateString):
    try:
        findDate = re.split('([0-9]{4})', dateString)
        if len(findDate) == 0:
            return -1
        finalDate = findDate[0]
        if len(findDate) > 1:
            finalDate = findDate[1]
        findIrregularDate = re.split('[0-9]{1,2}[/-]{1}[0-9]{1,2}[/-]{1}([0-9]{1,4})', finalDate)
        dateAnswer = finalDate
        if len(findIrregularDate) > 0:
            dateAnswer = findIrregularDate[0]
            if len(findIrregularDate) > 1:
                dateAnswer = findIrregularDate[1]
        try:
            dateAnswer = int(dateAnswer)
        except:
            dateAnswer = -1
        if dateAnswer < 100:
            if dateAnswer < 19:
                dateAnswer = 2000 + dateAnswer
            else:
                dateAnswer = 1900 + dateAnswer
        return dateAnswer
    except:
        return -1

# given a collection, assigns a rights uri address for each item in the collection.
# Matches item's date < 1922 to 'COPYRIGHT_NOT_EVALUATED' and >= 1922 to 'IN_COPYRIGHT'
def fixRightsURI(collection):
    rightsURI = collection['Rights URI']
    dates = collection['Date-EDTF']
    inferedCollectionDate = inferCollectionDate(collection)
    for num in range(0, len(rightsURI)):
        dateString = dates[num]
        if dateString == '':
            dateString = inferedCollectionDate
        formattedDate = normalizeDate(dateString)
        if formattedDate < 1922:
            rightsURI[num] = COPYRIGHT_NOT_EVALUATED
        else:
            rightsURI[num] = IN_COPYRIGHT
    reportField(collection, 'Rights URI')

# pre: normalizeType has been run on the collection, or every Type/Type-DCMI field is filled
# post: fills the Object Type field for every row of the collection, inferring it from the
#       other types already there, or maps it from Type/Type-DCMI field
def fixObjectType(collection):
    typeMatch = {'StillImage' : 'image', 'MovingImage' : 'Video', 'Text' : 'Text', 'Sound' : 'audio'}
    objectType = collection['Object Type']
    notAvailable = []
    inferedFieldString = ""
    colkeys = list(collection.keys())
    for num in range(0, len(objectType)):
        thisObjectType = objectType[num]
        if thisObjectType == "":
            if inferedFieldString == "":
                notAvailable.append(num)
            else:
                objectType[num] = inferedFieldString
        else:
            if inferedFieldString == "":
                inferedFieldString = thisObjectType
    for each in notAvailable:
        if inferedFieldString == "":
            typeColumnName = 'Type' if 'Type' in colkeys else 'Type-DCMI'
            inferredType = collection[typeColumnName][0]
            objectType[each] = typeMatch[inferredType]
        else:
            objectType[each] = inferedFieldString
    reportField(collection, 'Object Type')

# check that every row for a field is filled.
def checkField(collection, fieldName):
    collectionField = collection[fieldName]
    count = 0
    for each in collectionField:
        if each == "":
            print(count)
            return False
        count += 1
    return True

# prints a message reporting if field has all rows filled or not
def reportField(collection, fieldName):
    ok = checkField(collection, fieldName)
    if ok == True:
        print(bcolors.OKGREEN + fieldName + " was successfully normalized")
    else:
        print(bcolors.FAIL + fieldName + " normalization failed")


# given a collection and a filename, writes the collection to the file
# preserving csv format
def writeCsv2File(collection, filename):
    colkeys = list(collection.keys())
    writeStream = csv.writer(open(filename, 'w'), quoting=csv.QUOTE_MINIMAL, delimiter=',')
    # for num in (1, len(colkeys)):
    #     writeStream.writerow("\t" + colkeys[num])
    writeStream.writerow(colkeys)
    defaultColumnLength = len(collection[colkeys[0]])
    for num in range(0, defaultColumnLength):
        thisRow = []
        for each in colkeys:
            thisRow.append(collection[each][num])
        writeStream.writerow(thisRow)


# for Galloway project only; takes the item id info from the dc.identifier.other field
# and inserts right after the title in the dc.title field, in parentheses.
def insertItemIdIntoTitle(collection):
    defaultColumnLength = len(collection[list(collection.keys())[0]])
    for num in range(0, defaultColumnLength):
        titleField = collection['dc.title[]']
        titleItem = titleField[num]
        if titleItem == "":
            titleField = collection['dc.title[en_US]']
            titleItem = titleField[num]
        itemInfo = collection['dc.identifier.other[]'][num]
        if (len(itemInfo) == 0):
            itemInfo = collection['dc.identifier.other[en_US]'][num]
        itemData = itemInfo.split("||")
        if len(itemData) < 3:
            itemData = itemInfo.split(";")
        itemId = itemData[1]
        newTitle = titleItem + " (" + itemId + ")"
        titleField[num] = newTitle
    writeCsv2File(collection, os.path.join("export/", "gal-final3.csv"))

# checks and signals in red if the collection contains any fields such that its
# rows are not of the same length as the other fields'
def checkColConsistency(collection):
    colkeys = list(collection.keys())
    defaultLen = len(collection[colkeys[0]])
    notPrinted = True
    for each in colkeys:
        if (len(collection[each]) != defaultLen and notPrinted):
            print(bcolors.FAIL + " collection is inconsistent")
            notPrinted = False
    return notPrinted == True

# reads the fields that were modified from the collection, and writes a new .csv file
# containing a list of itemId,fieldnickname,fieldValue for each of the items and modified
# fields in the collection.
def writeModifiedFieldsData(collectionName, collection, fileName):
    print(bcolors.OKBLUE + "Generating metadata file " + fileName + " ...")
    lookForFields = ['Date-EDTF', 'Type-DCMI', 'Object Type', 'Restrictions', 'Rights URI', 'Digital Collection']
    fieldsMetadata = contentdm_api.getCollectionFieldInfo(collectionName)
    fieldsNickNameDict = collections.OrderedDict()
    for each in lookForFields:
        for field in fieldsMetadata:
            if each == field['name']:
                fieldsNickNameDict[each] = field['nick']
    colkeys = list(collection.keys())
    defaultColumnLength = len(collection[colkeys[0]]) # number of records for that collection
    writeStream = csv.writer(open(fileName, 'w'), quoting=csv.QUOTE_MINIMAL, delimiter=",")

    # first, we need to write the header to the file.
    # header = record number, (n1, n2, ...), for n1, n2, ... the modified fields' nicknames
    header = ["record number"]
    for fieldnickname in list(fieldsNickNameDict.values()):
        header.append(fieldnickname)
    writeStream.writerow(header)

    # now write the values
    for num in range (0, defaultColumnLength):
        line = [collection['CONTENTdm number'][num]]
        for field in lookForFields:
            fieldnickname = fieldsNickNameDict[field]
            try:
                line.append(collection[field][num])
            except:
                line.append(str(collection[field][num], errors='replace'))
        writeStream.writerow(line)

# given a collection, an old and a new field name, copies the content from the old field,
# and creates a new field with the cotnents of the old field in it. Then, removes the
# old field and its contents from the collection
def changeFieldname(collection, old, new):
    oldFieldData = collection[old]
    addFieldToCol(collection, new)
    for num in range(0, len(oldFieldData)):
        collection[new][num] = oldFieldData[num]
    del collection[old]

def main():
    col = mapDataToCollection("text/loc.txt")
    fieldsMetadata = contentdm_api.getCollectionFieldInfo("loc")
    reconstructDesc(col, fieldsMetadata)

    # --------- HERE --------

    # collectionsAnneWants = []
    # with open("collections-for-daniel-to-update.txt", 'r') as f:
    #     for line in f:
    #         collectionsAnneWants.append(line.strip())
    #
    # mappedDict = dict()
    # allColsList = contentdm_api.getCollectionList()
    # for each in allColsList:
    #     alias = each['alias'].split('/')[1]
    #     name = each['name']
    #     mappedDict[alias] = name
    #
    # requiredFields = ['Date-EDTF', 'Object Type', 'Restrictions', 'Rights URI', 'Digital Collection']
    #
    # for eachFile in os.listdir("./text"):
    #     if eachFile.endswith(".txt"):
    #         colName = eachFile.split('.')[0]
    #         if mappedDict[colName] in collectionsAnneWants:
    #             print bcolors.OKBLUE + "Processing " + eachFile + " ..."
    #             fullFileName = os.path.join("./text", eachFile)
    #             col = mapDataToCollection(fullFileName)
    #             consistent = checkColConsistency(col)
    #             if consistent:
    #                 colkeys = col.keys()
    #                 for each in requiredFields:
    #                     if each not in colkeys:
    #                         addFieldToCol(col, each)
    #                 if 'Type' in colkeys:
    #                     changeFieldname(col, 'Type', 'Type-DCMI')
    #                 else:
    #                     addFieldToCol(col, 'Type-DCMI')
    #
    #                 normalizeType(col)
    #                 fixObjectType(col)
    #                 fixRestrictions(col)
    #                 fixDigitalCollection(col, mappedDict[alias])
    #                 fixRightsURI(col)
    #                 exportFileName = eachFile.split(".")[0] + ".csv"
    #                 writeCsv2File(col, os.path.join("export-csv/", exportFileName))
    #                 writeModifiedFieldsData(colName, col, os.path.join("export-csv/", colName + "-csvMetadata.csv"))
    #             else:
    #                 print bcolors.FAIL + " check manually."
    #             print "\n"

if __name__ == '__main__':
    main()
