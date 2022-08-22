# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import sqlite3
import json

# %%
import sys
sys.path.append("../../data/")
sys.path.append("../")

# %%
import pandas as pd

# %%
import pprint

# %%
import globalStore.constants as constants

# %%
from lib.port_utils import getDataFromZoteroDatabases

# %%
zotero_dp = constants.ZOTERO_DATABASE_PATH
zotero_dp

# %%
bbib_dp = constants.BETTER_BIBTEX_SEARCH_PATH
bbib_dp

# %%
conn = sqlite3.connect(zotero_dp)
conn2 = sqlite3.connect(bbib_dp)
# conn2

# %%
cur = conn.cursor()
cur2 = conn2.cursor()

# %%
data = cur2.execute("SELECT * from citeKeys").fetchall()

# %%
data = pd.DataFrame(data, columns=['itemID', 'libraryID', 'itemKey', 'citeKey'])
data.head()


# %%
def prettyAttachment(idx, it_type, it_path):
    if it_type is None or it_path is None:
        return ''
    elif 'office' in it_type:
        return '(' + str(idx) + ') ' + it_type.split('.')[-1] + ' - ' + it_path.split(':')[-1] 
    else:
        return '(' + str(idx) + ') ' + it_type.replace('application/','') + ' - ' + it_path.split(':')[-1] 
        # return 


# %% tags=[]
itemList = []
for index, (itemID, libraryID, itemKey, citeKey) in data.iterrows(): 
    if itemID == 34:
        itemDict = {'itemID': itemID, 'libraryID': libraryID, 'itemKey': itemKey, 'citeKey': citeKey}
        print(citeKey)
        creaters = cur.execute(item_creators_sql, (itemID,)).fetchall()
        # print(creaters)
        authors = ', '.join([' '.join(it) for it in creaters])
        # print(bibtexAuthors)
        itemDict['authors'] = authors
        # print(authors)
        metadata = cur.execute(item_meta_data, (itemID, itemKey)).fetchall()
        # print(metadata)
        itemDict['itemType'] = metadata[0][0]
        itemDict['dateAdded'] = metadata[0][1]
        itemDict['dateModified'] = metadata[0][2]
        itemDict['clientDateModified'] = metadata[0][3]
        # print(metadata)
        # print(itemID)
        tagList = cur.execute(item_tag_data, (itemID,)).fetchall()
        tags = ', '.join([it[0] for it in tagList])
        itemDict['tags'] = tags
        # print(tags)
        fieldValues = cur.execute(item_field_data, (itemID,)).fetchall()
        for (fName, fValue) in fieldValues:
            if fName == 'date':
                fValue = fValue.split(' ')[0]
            if fName == 'abstractNote':
                fValue = fValue[:1995] + ' ...'
            itemDict[fName] = fValue
            
        itemDict['year'] = itemDict['date'].split('-')[0]
        print(itemDict['year'])
        
        collectionValues = cur.execute(item_collection_data, (itemID,)).fetchall()
        collectionNames = ', '.join([it[0] for it in collectionValues])
        # print(collectionNames)
        itemDict['collections'] = collectionNames
        
        # print(fieldValues)
        attachmentValues = cur.execute(item_attachment_data, (itemID,)).fetchall()
        # print(attachmentValues)
        # print('-----------')
        # attachments = '\n'.join(['(' + str(idx) + ') ' + prettyContentType(it_type) + ' - ' + it_path.split(':')[-1] for idx, (it_type, it_path) in enumerate(attachmentValues)])
        attachments = '\n'.join([prettyAttachment(idx, it_type, it_path) for idx, (it_type, it_path) in enumerate(attachmentValues)])
        itemDict['attachments'] = attachments
        # print(attachments)
        
        bibtexAuthors = ' and '.join([it[1] + ', ' + it[0] for it in creaters])
        
        bibtex = '@article{' + itemDict['citeKey'] + ', \n' + \
            '\t' + 'author = {' + bibtexAuthors + '}, \n' + \
            '\t' + 'journal = {' + itemDict['publicationTitle'] + '}, \n' + \
            '\t' + 'title = {' + itemDict['title'] + '}, \n' + \
            '\t' + 'year = {' +  itemDict['year'] + '} \n' + '}'
        
        itemDict['bibtex'] = bibtex
        # print(bibtex)
        
        print('-----------')
        itemList.append(itemDict)
        pprint.pprint(itemDict)

# %% jupyter={"outputs_hidden": true} tags=[]
itemList = getDataFromZoteroDatabases()

# %%
len(itemList)

# %%
itemList[0]

# %%
import arrow
arr = arrow.get(itemList[0]['clientDateModified'])

# %%
arr

# %%
arr.time()

# %%
arr.month

# %%
cur.close()
cur2.close()

# %%
conn.close()
conn2.close()

# %%
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

# %%
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

# %%
# given an item id, get its tags
item_tag_data = """
SELECT
    t.name
FROM
    itemTags as it left join tags as t on it.tagID = t.tagID
WHERE
    it.itemID = ?
"""

# %%
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

# %%
# given an item id, get its attachment info
item_attachment_data = """
SELECT
    ia.contentType, ia.path
FROM
    itemAttachments as ia
WHERE
    ia.parentItemID = ?
"""

# %%
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

# %%
from notion_client import Client
from lib.port_utils import getDataFromZoteroDatabases, portZoteroDataToNotion, getNotionPageEntryFromPropObj, getAllRowsFromNotionDatabase

# %%
import globalStore.constants as constants

# %%
with open(constants.NOTION_SECRET_FILE, "r") as f:
    secrets_notion = json.load(f)

# %%
# initialize notion client and determine notion DB
notion = Client(auth = secrets_notion['notionToken'])
notionDB_id = secrets_notion['databaseID']

# %% tags=[] jupyter={"outputs_hidden": true}
zoteroDataList = getDataFromZoteroDatabases()

# %%
len(zoteroDataList)

# %%
zoteroDataList[1]

# %%

# %%

# %%
allNotionRows = getAllRowsFromNotionDatabase(notion, notionDB_id)

# %%
portZoteroDataToNotion(zoteroDataList, notion, notionDB_id)

# %%
