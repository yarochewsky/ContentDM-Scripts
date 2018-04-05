# University of Washington Digital Strategies, Winter '18
# Daniel Fonseca Yarochewsky

# This module takes in a formatted metadata file, output from excel.py, and modifies
# the cached files from ContentDM Project Client. In particular, for each record in the collection,
# it updates all values for the field nicknames specified in the metadata file. For more details
# on the structure of this metadata file, check the excel library (excel.py). Note that the
# ContentDM Client cached files should be in the same directory as this module, and ALL of the
# files that are specified in the metadata file have to be cached already.


import csv, os, shutil
import xml.etree.ElementTree as ET
import collections


# given the csv reader object, creates and populates a new dictionary
# containing record numbers as keys, and dictionary of fields as values
# each of these dictionaries of fields bears the field's nickname as a key,
# and the field's value for that record
def populateMap(reader):
	filesDict = dict()
	header = []

	# the first element in the reader is the header
	for num in range(1, len(reader[0])): # we throw away the first one because it's the record number
		header.append(reader[0][num])

	# then, each subsequent element in the reader is a row of values, following the same
	# order of the header's field names
	for num in range(1, len(reader)):
			eachRecord = reader[num]
			# the first element is the record number.
			recordNumber = eachRecord[0]
			# we create an OrderedDict for each record number
			filesDict[recordNumber] = collections.OrderedDict()
			# then, each subsequent element in the record array is a value of the specified fields
			# in the header we read. These are the key-value mappings
			for fieldNum in range(1, len(eachRecord)):
				filesDict[recordNumber][header[fieldNum - 1]] = eachRecord[fieldNum]
	return filesDict

# given a record name, finds the contentdm cached file for that record,
# in the current directory, and returns the tree object of that file.
# Returns None if file does not exist (has not been cached)
def findXMLRoot(record):
	contentdmCachedFilename = record + ".desc"
	if (os.path.isfile(contentdmCachedFilename)):
		xmlTree = ET.parse(contentdmCachedFilename)
		return xmlTree
	else:
		return None

# given an XML tree root, a field nickname, and a new field value,
# seaches for the field in the XML tree, and updates the field value
# with the new provided value
def updateFieldInXML(root, nickname, value):
	findElement = root.find(nickname)
	if findElement != None:
		print(" Writing " + nickname + " as " + value)
		saveOld = findElement.text
		if saveOld == None:
			findElement.set('old', "None")
		else:
			findElement.set('old', saveOld)
		findElement.text = value

# creates a backup dir to copy over the contentdm cached files .desc
# to that directory
def backupCachedFiles():
	if not os.path.exists("./backup"):
		os.makedirs("./backup")
	for eachFile in os.listdir("."):
		if eachFile.endswith(".desc"):
			print("Copying file : " + eachFile + " to backup directory ...")
			shutil.copy(eachFile, "./backup")

def main():

	# tree = ET.parse("255.xml")
	# for each in tree.iter():
	# 	print each.tag
	# 	print(ET.tostring(each))
	content = []
	with open("255.xml", "r") as f:
		content = f.read()
	with open("255.xml", "w") as f:
		f.write("<?xml version\"1.0\" encoding=\"utf-8\"?>\n")
		f.write(content)
	


	# HERE ----
	# filename = input("Please, enter the name of the metadata file ")
	# backupCachedFiles() # backup every cached file before writing anything to the originals
	# with open(filename, 'r') as inputFile:
	# 	reader = list(csv.reader(inputFile, delimiter=","))
	#
	# recordsDict = populateMap(reader)
	# records = list(recordsDict.keys())
	# for record in records:
	# 		treeRoot = findXMLRoot(record)
	# 		if (treeRoot != None):
	# 			recordFields = recordsDict[record]
	# 			print("Updating record number " + record + " ...")
	# 			for recordFieldsNickname in list(recordFields.keys()):
	# 				filedValueInRecord = recordFields[recordFieldsNickname]
	# 				updateFieldInXML(treeRoot, recordFieldsNickname, filedValueInRecord)
	# 			treeRoot.write(record + ".desc", encoding="utf-8", xml_declaration=False,
	# 						   method="xml", short_empty_elements=False)
	# 		else:
	# 			print("Record file " + record + " is not cached or does not exist ...")

if __name__ == '__main__':
	main()
