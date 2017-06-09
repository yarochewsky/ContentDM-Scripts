# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import contentdm_api, os, sys, re

# This program is a solution for compound objects in ContentDM. We recommend
# deprecation of ContentDM compound objects due to their odd behavior on
# retrieval of data, using frontend applications, as well as maintainable
# and scalable database structure for the future. You should "uncompound" your
# compound objects in your collection using this tool. This program specifically,
# generates metadata for the new uncompound object, aggregating all the data
# from the parts that make up the compound object into one single new file.
# It also selects the new order number and thumbnail for the new file and saves
# in the same folder.

# Author: Daniel Fonseca Yarochewsky
# Spring '17

# change your collection name here
COLLECTION_NAME = "filmarch"

# asks for a file directory name to save the new metadata for the uncompound
# item, and then for the ContentDM numbers of the files to be uncompounded.
# Proceeds to donwload the file metadata and merges them, as well as downloads
# the thumbnail for the main compound object file, to be the new thumbnail
# for the new item. The order number of the new file is the lower order number
# found among the files inside the compound object. The duration of the new item
# is a cumulative sum of the duration of all the available files, and such is for
# all the cumulative data fields found in the compound object. Mianly, notes,
# locations, participants. Note that duplicates are thrown away for any given
# field.
def main():
    print 'Welcome to the solution for ContentDM compound objects!'
    print 'Written by Daniel Fonseca Yarochewsky'
    print 'This program will create a folder in the current directory with the desired name, '
    print 'containing the metadata merged from all of the items inside the compound object'

    files = int(raw_input("How many files are you processing today? "))
    for each in range(0, files):
        fileName = str(raw_input("Type a filename for the new merged item: "))
        print ""
        mergedFileName = os.path.join('./', fileName)
        createFolderStructure(mergedFileName)
        objs = []
        option = raw_input("Are you specifying sequential ContentDM numbers? (y/n) ")
        if(option == 'y' or option == 'Y'):
            cpdNumber = int(raw_input("Enter the compound object ContentDM number: "))
            lowerBound = int(raw_input("Enter the ContentDM number of the first item in the compound object: "))
            upperBound = int(raw_input("Enter the ContentDM number of the last item in the compound object: "))
            for num in range(lowerBound, upperBound + 1):
                saveContentDmFile(num, objs)
            saveContentDmFile(cpdNumber, objs)
            saveThumbnail(cpdNumber, mergedFileName)

        else:
            numberOfFiles = int(raw_input("How many files are you merging? "))
            item = int(raw_input("Enter the ContentDM number for the file " +
                       "1 out of " + str(numberOfFiles) + " "))
            saveContentDmFile(item, objs)
            saveThumbnail(item, mergedFileName)
            for num in range(2, numberOfFiles + 1):
                item = int(raw_input("Enter the ContentDM number for the file " +
                           str(num) + " out of " + str(numberOfFiles) + " "))
                saveContentDmFile(item, objs)

        gatherItemInfo(objs, mergedFileName)
        print 'Done! You are now ready to uncompound! Good luck, son'
        print "\n"
    print "Bye... Thanks for using this software to make you collection a better place!"

# given an item number and a file path of the directory, saves the thumbnail
# for the file number into the working directory
def saveThumbnail(item, path):
    thumbnailFilename = str(item) + '.jpg'
    print "Saving thumbnail " + thumbnailFilename + " ..."
    contentdm_api.getItemThumbnail(COLLECTION_NAME, item, thumbnailFilename)
    os.rename(os.path.join("./", thumbnailFilename), os.path.join(path, thumbnailFilename))

# given an item number and an objects array, retrieves and saves the ContentDM
# file to the objects array
def saveContentDmFile(item, objs):
    print 'Merging metadata for ContentDM number ' + str(item) + '...'
    objs.append(contentdm_api.getItemInfo(COLLECTION_NAME, item))


# given an objects array of ContentDM file objects, and a path directory to save
# metadata information, saves text files with the required data fields to uncompound
# the compound object
def gatherItemInfo(objs, path):
    duration = 0
    durationString = ''
    clipSource = ''
    originalSourceSummary = ''
    clipDescriptions = ''
    participants = []
    notes = []
    subjectsLCTGM = ''
    subjectsLCSH = []
    location = ''
    dateCreated = ''
    datesCreated = ''
    earliestDateCreated = ''
    latestDateCreated = ''
    language = ''
    digitalCollection = ''
    orderNumber = []
    orderingInfo = ''
    repository = ''
    repositoryCollection = ''
    repositoryCollectionGuide = ''
    digitalReproductionInformation = ''
    contributor = ''
    rights = ''
    fileType = ''
    adminNotes = ''
    institution = ''
    cataloging = ''

    for obj in objs:
        if('filmvi' in obj and len(obj['filmvi']) > 0):
            originalSourceSummary = obj['filmvi']
        if('clip' in obj and len(obj['clip']) > 0):
            clipDescriptions += obj['clip'] + '\n'
        if('creato' in obj and len(obj['creato']) > 0):
            clipSource = obj['creato']
        if('partic' in obj and len(obj['partic']) > 0):
            particList = obj['partic'].split("<br>")
            for p in particList:
                if (p.strip() not in participants):
                    participants.append(p.strip())
        if('notes' in obj and len(obj['notes']) > 0):
                note = obj['notes'].strip()
                if(note not in notes):
                    notes.append(note)
        if('subjeb' in obj and len(obj['subjeb']) > 0):
            subjectsLCTGM = obj['subjeb']
        if('subjea' in obj and len(obj['subjea']) > 0):
            subejctsList = obj['subjea'].split(";")
            for s in subejctsList:
                if(s.strip() not in subjectsLCSH):
                    subjectsLCSH.append(s.strip())
        if('locati' in obj and len(obj['locati']) > 0):
            location += obj['locati']
        if('type' in obj and len(obj['type']) > 0):
            dateCreated = obj['type']
        if('format' in obj and len(obj['format']) > 0):
            datesCreated = obj['format']
        if('source' in obj and len(obj['source']) > 0):
            latestDateCreated = obj['source']
        if('identi' in obj and len(obj['identi']) > 0):
            earliestDateCreated = obj['identi']
        if('langub' in obj and len(obj['langub']) > 0):
            language = obj['langub']
        if('digita' in obj and len(obj['digita']) > 0):
            digitalCollection = obj['digita']
        if(('order' in obj and len(obj['order']) > 0)):
            orderNumber.append(obj['order'])
        if('orderi' in obj and len(obj['orderi']) > 0):
            orderingInfo = obj['orderi']
        if('reposi' in obj and len(obj['reposi']) > 0):
            repository = obj['reposi']
        if('reposa' in obj and len(obj['reposa']) > 0):
            repositoryCollection = obj['reposa']
        if('reposb' in obj and len(obj['reposb']) > 0):
            repositoryCollectionGuide = obj['reposb']
        if('digitb' in obj and len(obj['digitb']) > 0):
            digitalReproductionInformation = obj['digitb']
        if('contra' in obj and len(obj['contra']) > 0):
            contributor = obj['contra']
        if('righta' in obj and len(obj['righta']) > 0):
            rights = obj['righta']
        if('typa' in obj and len(obj['typa']) > 0):
            fileType = obj['typa']
        if('admini' in obj and len(obj['admini']) > 0):
            adminNotes = obj['admini']
        if('instit' in obj and len(obj['instit']) > 0):
            institution = obj['instit']
        if('catalo' in obj and len(obj['catalo']) > 0):
            cataloging = obj['catalo']
        if('durati' in obj and len(obj['durati']) > 0):
            clipDuration = obj['durati']
            durationPattern = r"([0-9]{0,2})([ ]*)?min([., ]*)?([0-9]{0,2})?"
            regexDuration = re.search(durationPattern, clipDuration)
            minutes = 0
            seconds = 0
            if(regexDuration):
                if(regexDuration.group(1)):
                    minutes = int(regexDuration.group(1))
                if(regexDuration.group(4)):
                    seconds = int(regexDuration.group(4))
                duration += (seconds + (minutes * 60))

    # CREATING FILES:
    durationMinutes = (duration / 60)
    durationSeconds = (duration % 60)
    minutesString = str(durationMinutes)
    secondsString = str(durationSeconds)
    if(durationSeconds == 0):
        secondsString = '00'
    if(durationMinutes == 0):
        minutesString = '00'
    durationString = str(minutesString) + " min.," + str(secondsString) + " sec."
    createFile(path, 'duration.txt', durationString)
    # summary is conglomerate of clip summaries and original compound summary
    summary = originalSourceSummary + ' \n' + clipDescriptions
    createFile(path, 'order.txt', min(orderNumber))

    noteString = ""
    for note in notes:
        noteString += str(note) + " \n"
    createFile(path, 'notes.txt', noteString)

    participantsString = ""
    if(len(participants) > 0):
        participantsString += participants[0]
        participants.remove(participants[0])
    for participant in participants:
        participantsString += "<br>" + participant
    createFile(path, 'participants.txt', participantsString)


    subjectsLCSHString = ""
    if(len(subjectsLCSH) > 0):
        subjectsLCSHString += subjectsLCSH[0]
        subjectsLCSH.remove(subjectsLCSH[0])
    for subject in subjectsLCSH:
        subjectsLCSHString += ";" + subject
    createFile(path, 'subjects_LCSH.txt', subjectsLCSHString)

    createFile(path, 'summary.txt', summary)
    createFile(path, 'subjects_LCTGM.txt', subjectsLCTGM)
    createFile(path, 'date_created.txt', dateCreated)
    createFile(path, 'location.txt', location)
    createFile(path, 'earliest_day_created.txt', earliestDateCreated)
    createFile(path, 'dates_created.txt', datesCreated)
    createFile(path, 'ordering_info.txt', orderingInfo)
    createFile(path, 'digital_collection.txt', digitalCollection)
    createFile(path, 'language.txt', language)
    createFile(path, 'latest_day_created.txt', latestDateCreated)
    createFile(path, 'repository.txt', repository)
    createFile(path, 'repository_collection.txt', repositoryCollection)
    createFile(path, 'repository_collection_guide.txt', repositoryCollectionGuide)
    createFile(path, 'digital_reproduction_info.txt', digitalReproductionInformation)
    createFile(path, 'contributor.txt', contributor)
    createFile(path, 'rights.txt', rights)
    createFile(path, 'administrative_notes.txt', adminNotes)
    createFile(path, 'type.txt', fileType)
    createFile(path, 'institution.txt', institution)
    createFile(path, 'cataloging.txt', cataloging)
    createFile(path, 'source_of_clip.txt', clipSource)

# creates folders to enclose the generated metadata in the current directory
# folder structure tree created is as follows:
# .metadata
def createFolderStructure(path):
    os.mkdir(path, 0755)

# createas a file, or appends to the end of it, given a path, a field name
# that is going to be the nam eof the file in that directory, and a data string
# to write to the file
def createFile(path, field, data):
    filename = os.path.join(path, field)
    with open(filename, 'a') as f:
        f.write(data)

if __name__ == '__main__':
    main()
