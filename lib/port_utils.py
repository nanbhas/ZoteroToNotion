  
"""
Author: Nandita Bhaskhar
Zotero to Notion helper functions
"""

import os
import sys
sys.path.append('../')

import time
import arrow
import json

from tqdm import tqdm

import sqlite3
import pandas as pd

import globalStore.constants as constants

############################
#  SQL Queries for Zotero
############################

# given an item id, get its meta data
item_meta_data = """
SELECT
    it.typeName, i.dateAdded, i.dateModified, i.clientDateModified 
FROM
    items as i left join itemTypes as it on i.itemTypeID = it.itemTypeID
WHERE
    i.itemID = ? and
    i.key = ? 
"""

# given an item id, get a list of its authors
item_creators_sql = """
SELECT
    c.firstName, c.lastName
FROM
    itemCreators as ic, creators as c
WHERE
    ic.creatorID = c.creatorID and
    ic.itemID = ?
ORDER BY
    ic.orderIndex
"""

# given an item id, get its tags
item_tag_data = """
SELECT
    t.name
FROM
    itemTags as it left join tags as t on it.tagID = t.tagID
WHERE
    it.itemID = ?
"""

# given an item id, get its field values and data 
item_field_data = """
SELECT
    f.fieldName, idv.value
FROM
    itemData as id 
    left join itemDataValues as idv on id.valueID = idv.valueID
    left join fields as f on id.fieldID = f.fieldID
WHERE
    id.itemID = ? and 
    (f.fieldID = 1 or 
    f.fieldID = 2 or
    f.fieldID = 6 or 
    f.fieldID = 13 or 
    f.fieldID = 37)
ORDER BY
    f.fieldID
"""

# given an item id, get its attachment info
item_attachment_data = """
SELECT
    ia.contentType, ia.path
FROM
    itemAttachments as ia
WHERE
    ia.parentItemID = ?
"""

# given an item id, get its collection info
item_collection_data = """
SELECT
    c.collectionName, c.key 
FROM
    collectionItems as ci 
    left join collections as c on c.collectionID = ci.collectionID
WHERE
    ci.itemID = ?
"""

############################

def prettyAttachment(idx, it_type, it_path):
    '''
    string manipulation for attachment info
    '''
    if it_type is None or it_path is None:
        return ''
    elif 'office' in it_type:
        return '(' + str(idx) + ') ' + it_type.split('.')[-1] + ' - ' + it_path.split(':')[-1] 
    else:
        return '(' + str(idx) + ') ' + it_type.replace('application/','') + ' - ' + it_path.split(':')[-1] 


def getDataFromZoteroDatabases(zoteroDBFile: str = constants.ZOTERO_DATABASE_PATH, 
                        betterBibDBFile: str = constants.BETTER_BIBTEX_SEARCH_PATH):
    '''
    Gets all data from Zotero databases
    Args:
        zoteroDBFile: (str) path to the Zotero database
        betterBibDBFile: (str) path to the Better Bibtex Search database
    Returns:
        zoteroData: (list of dicts) Each item in list is a dict corresponding to a document in Zotero
    '''
    # establish connection via sqlite3
    conn = sqlite3.connect(zoteroDBFile)
    conn2 = sqlite3.connect(betterBibDBFile)

    # get cursor objects
    cur = conn.cursor()
    cur2 = conn2.cursor()

    # get all item ids from better bibtex search database
    data = cur2.execute("SELECT * from citeKeys").fetchall()

    zoteroData = []

    # loop over items
    for itemID, libraryID, itemKey, citeKey in data: 

        # get initial fields for item
        itemDict = {'UID': itemKey, 'Citation': citeKey}
        # print(citeKey)

        # get authors
        creaters = cur.execute(item_creators_sql, (itemID,)).fetchall()
        authors = ', '.join([' '.join(it) for it in creaters])
        itemDict['Authors'] = authors

        # get metadata
        metadata = cur.execute(item_meta_data, (itemID, itemKey)).fetchall()
        itemDict['Type'] = metadata[0][0]
        itemDict['Created At'] = metadata[0][1]
        itemDict['Last Modified At'] = metadata[0][2]
        # itemDict['clientDateModified'] = metadata[0][3]
        
        # get tags
        tagList = cur.execute(item_tag_data, (itemID,)).fetchall()
        tags = ', '.join([it[0] for it in tagList])
        itemDict['Zotero Tags'] = tags
        
        # get various field values (title, venue, etc) and data
        fieldValues = cur.execute(item_field_data, (itemID,)).fetchall()
        for (fName, fValue) in fieldValues:
            if fName == 'title':
                itemDict['Title'] = fValue
            if fName == 'abstractNote':
                itemDict['Abstract'] = fValue[:1995] + ' ...' # notion can only handle 2000 characters 
            if fName == 'date':
                date = fValue.split(' ')[0] # not used in Notion
            if fName == 'url':
                itemDict['URL'] = fValue
            if fName == 'publicationTitle':
                itemDict['Venue'] = fValue

        # extract year from date field    
        itemDict['Year'] = date.split('-')[0]

        # get collection info
        collectionValues = cur.execute(item_collection_data, (itemID,)).fetchall()
        collectionNames = ', '.join([it[0] for it in collectionValues])
        itemDict['Collection Names'] = collectionNames
            
        # get attachments
        attachmentValues = cur.execute(item_attachment_data, (itemID,)).fetchall()
        attachments = '\n'.join([prettyAttachment(idx, it_type, it_path) for idx, (it_type, it_path) in enumerate(attachmentValues)])
        itemDict['Filename'] = attachments  
        
        # get bibtex value
        bibtexAuthors = ' and '.join([it[1] + ', ' + it[0] for it in creaters])
        bibtex = '@article{' + itemDict['Citation'] + ', \n' + \
            '\t' + 'author = {' + bibtexAuthors + '}, \n' + \
            '\t' + 'journal = {' + itemDict['Venue'] + '}, \n' + \
            '\t' + 'title = {' + itemDict['Title'] + '}, \n' + \
            '\t' + 'year = {' +  itemDict['Year'] + '} \n' + '}'
        itemDict['BibTex'] = bibtex
        
        # print('-----------')
        zoteroData.append(itemDict)
    
    return zoteroData


def getNotionPageEntryFromPropObj(propObj):
    '''
    Format the propObj dict to Notion page format
    Args:
        propObj: (dict)
    Returns:
        newPage: (Notion formated dict)
    '''
    
    dateKeys = {'Created At', 'Last Modified At'}
    urlKeys = {'URL'}
    titleKeys = {'Citation'}
    textKeys = set(propObj.keys()) - dateKeys - titleKeys - urlKeys
    newPage = {
        "Citation": {"title": [{"text": {"content": propObj['Citation']}}]}
    }
    
    for key in textKeys:
        newPage[key] = {"rich_text": [{"text": { "content": propObj[key]}}]}    
    
    for key in dateKeys:
        newPage[key] = {"date": {"start": propObj[key] }}
        
    for key in urlKeys:
        try:
            newPage[key] = {"url": propObj[key]}
        except:
            pass
    
    return newPage
    

def getAllRowsFromNotionDatabase(notion, notionDB_id):
    '''
    Gets all rows (pages) from a notion database using a notion client
    Args:
        notion: (notion Client) Notion client object
        notionDB_id: (str) string code id for the relevant database
    Returns:
        allNotionRows: (list of notion rows)

    '''
    start = time.time()
    hasMore = True
    allNotionRows = []
    i = 0

    while hasMore:
        if i == 0:
            try:
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    #"filter": {"property": "UID", "text": {"equals": it.id}},
                                }
                            )
            except:
                print('Sleeping to avoid rate limit')
                time.sleep(30)
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    #"filter": {"property": "UID", "text": {"equals": it.id}},
                                }
                            )
                
        else:
            try:
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    "start_cursor": nextCursor,
                                    #"filter": {"property": "UID", "text": {"equals": it.id}},
                                }
                            )
            except:
                print('Sleeping to avoid rate limit')
                time.sleep(30)
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    "start_cursor": nextCursor,
                                    #"filter": {"property": "UID", "text": {"equals": it.id}},
                                }
                            )
            
        allNotionRows = allNotionRows + query['results']
        nextCursor = query['next_cursor']
        hasMore = query['has_more']
        i+=1

    end = time.time()
    print('Number of rows in notion currently: ' + str(len(allNotionRows)))
    print('Total time taken: ' + str(end-start))

    return allNotionRows


def portZoteroDataToNotion(zoteroList, notion, notionDB_id):
    '''
    Port data from Zotero to Notion
    Args:
        zoteroList: (list of dicts) each dict is a zotero item
        notion: (notion Client) Notion client object
        notionDB_id: (str) string code id for the relevant database
    '''
    allNotionRows = getAllRowsFromNotionDatabase(notion, notionDB_id)
    print('Number of rows in notion currently: ' + str(len(allNotionRows)))

    for i, it in enumerate(tqdm(zoteroList)):        

        # to check if its UID is already in notion
        notionRow = [row for row in allNotionRows if row['properties']['UID']['rich_text'][0]['text']['content'] == it['UID']]
        
        # ensure not more than one match
        numMatches = len(notionRow)
        assert numMatches < 2, "Duplicates are present in the notion database"
        
        if numMatches == 1: # item already exists in Notion, need to update existing row

            notionRow = notionRow[0]

            zoteroLastModifiedTime = arrow.get(it['Last Modified At']) # zotero is local on laptop, so already in US/Pacific timezone
            notionTime = arrow.get(notionRow['last_edited_time']).to('US/Pacific')

            # last modified time on Zotero is AFTER last edited time on Notion
            # if so, update Notion row
            if zoteroLastModifiedTime > notionTime:
                print('--------Updating row in notion')
                pageID = notionRow['id']
                propObj = it
                notionPage = getNotionPageEntryFromPropObj(propObj)
                try:
                    notion.pages.update( pageID, properties = notionPage)
                except:
                    print('Sleeping to avoid rate limit')
                    time.sleep(30)
                    notion.pages.update( pageID, properties = notionPage)

            else:
                print('--------Nothing to update') #TODO: Comment this out later
                pass

        elif numMatches == 0: # item does not exist in Notion, need to create new row

            print('----No results matched query. Creating new row')
            # extract properties and format it well
            propObj = it
            notionPage = getNotionPageEntryFromPropObj(propObj)
            try:
                notion.pages.create(parent={"database_id": notionDB_id}, properties = notionPage)
            except:
                print('Sleeping to avoid rate limit')
                time.sleep(30)
                notion.pages.create(parent={"database_id": notionDB_id}, properties = notionPage)

        else:
            raise NotImplementedError
