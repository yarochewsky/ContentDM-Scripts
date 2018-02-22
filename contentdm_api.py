# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# University of Washington, Special Collections, Spring 2017
# CONTENTDM MODULE

import requests, urllib, os
from requests.auth import HTTPBasicAuth

# replace api url here
URL_API_SERVER="http://server16786.contentdm.oclc.org/dmwebservices/index.php?q="
# replace site url here
URL_SITE="https://cdm16786.contentdm.oclc.org/utils/"
# url to download export file
SERVER_DOWNLOAD_COLLECTION = "https://server16786.contentdm.oclc.org/cgi-bin/admin/getfile.exe?CISOMODE=1&CISOFILE="
# place username here
USERNAME = ''
# place password here
PASSWORD = ''


# returns a list of all collections in the server
def getCollectionList(formatType="json"):
    collectionEndpoint = "dmGetCollectionList"
    fullUrl = (URL_API_SERVER + collectionEndpoint + "/" + formatType)
    return makeRequest(fullUrl, formatType)

# returns a list of all the fields metadata for a given collection name
def getCollectionFieldInfo(collectionName, formatType="json"):
    fieldInfoEndpoint = "dmGetCollectionFieldInfo/"
    fullUrl = (URL_API_SERVER + fieldInfoEndpoint + collectionName + "/" + formatType)
    return makeRequest(fullUrl, formatType)

# takes a collection name, and a query string, and returns the object
# resulting for that query
def query(collectionName, queryString, formatType="json"):
    queryEndpoint = "dmQuery"
    query = "0"
    if(queryString):
        query = "CISOSEARCHALL^" + queryString + "^all^and"
    fullUrl = (URL_API_SERVER + queryEndpoint + "/" + collectionName +
                "/" + query + "/fields/order/1024/0/0/0/0/0/0/0/" + formatType)
    return makeRequest(fullUrl, formatType)

# takes a collection name, and item id, and returns data about a
# compound object
def getCompoudObjectInfo(collectionName, itemId, formatType="json"):
    getCompoudEndpoint = "dmGetCompoundObjectInfo"
    fullUrl = (URL_API_SERVER + getCompoudEndpoint + "/" + collectionName +
                "/" + str(itemId) + "/" + formatType)
    return makeRequest(fullUrl, formatType)

# takes a collection name, item id (int), and desired format (json, or xml),
# and retrieves an object with the item's information
def getItemInfo(collectionName, itemId, formatType="json"):
    getItemEndpoint = "dmGetItemInfo"
    fullUrl = (URL_API_SERVER + getItemEndpoint + "/" + collectionName +
                "/" + str(itemId) + "/" + formatType)
    return makeRequest(fullUrl, formatType)

# takes a collection name, item id (int), and desired file path to save,
# and downloads the thumbnail of the video to the specified path
def getItemThumbnail(collectionName, itemId, fileName):
    get("getthumbnail", collectionName, itemId, fileName)

# takes a collection name, item id (int), filename, and desired file path to save,
# and downloads the video file to the specified path
def getFile(collectionName, itemId, fileName, pathName):
    get("getfile", collectionName, itemId, pathName + fileName)

# helper: downloads a file given endpoint, collection name, item id, and
#         filename
def get(endpoint, collectionName, itemId, fileName):
    fullUrl = (URL_SITE + endpoint + "/collection/"
                + collectionName + "/id/" + str(itemId))
    print "Downloading " + fileName + "  ..."
    r = urllib.urlretrieve(fullUrl, fileName)

# given a collection name, and a directory, downloads the collection original file from
# the server, and saves it in the directory as a text file with the filename = collection name
def downloadCollection(collectionName, directory):
    r = requests.get(SERVER_DOWNLOAD_COLLECTION + '/' + collectionName +
                     '/index/description/export.txt', auth=HTTPBasicAuth(USERNAME, PASSWORD))
    with open(os.path.join(directory, collectionName + ".txt"), 'w') as output:
        output.write(r.text)

# helper: returns a request in JSON, given url.
def makeRequest(fullUrl, formatType="json"):
    r = requests.get(fullUrl)
    if formatType == "xml":
        return r.text
    return r.json()
