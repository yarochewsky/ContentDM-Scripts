# University of Washington, Special Collections
# CONTENTDM MODULE
# Daniel Fonseca Yarochewsky

import requests, urllib

# replace api url here
URL_API_SERVER="http://server16786.contentdm.oclc.org/dmwebservices/index.php?q="
# replace site url here
URL_SITE="https://cdm16786.contentdm.oclc.org/utils/"


# takes a collection name, item id (int), and desired format (json, or xml),
# and retrieves an object with the item's information
def getItemInfo(collectionName, itemId, formatType="json"):
    getItemEndpoint = "dmGetItemInfo"
    fullUrl = (URL_API_SERVER + getItemEndpoint + "/" + collectionName +
                "/" + str(itemId) + "/" + formatType)
    r = requests.get(fullUrl)
    return r.json()

# takes a collection name, item id (int), and desired file path to save,
# and downloads the thumbnail of the video to the specified path
def getItemThumbnail(collectionName, itemId, fileName):
    get("getthumbnail", collectionName, itemId, fileName)

# takes a collection name, item id (int), and desired file path to save,
# and downloads the video file to the specified path
def getFile(collectionName, itemId, fileName):
    get("getfile", collectionName, itemId, fileName)

# helper: downloads a file given endpoint, collection name, item id, and
#         filename
def get(endpoint, collectionName, itemId, fileName):
    fullUrl = (URL_SITE + endpoint + "/collection/"
                + collectionName + "/id/" + str(itemId))
    r = urllib.urlretrieve(fullUrl, fileName)
