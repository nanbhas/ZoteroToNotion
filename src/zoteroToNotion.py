"""
Author: Nandita Bhaskhar
End-to-end script for getting updates from Zotero (local) on to the Notion Database of your choice
"""

import sys
sys.path.append("../")

import arrow
import time
import json

import globalStore.constants as constants

from notion_client import Client
from lib.port_utils import getDataFromZoteroDatabases, portZoteroDataToNotion
from lib.utils import *

# pass in arguments to run the script
PYTHON = sys.executable
parser = argparse.ArgumentParser()
parser.add_argument("--copyZotero", default=True, type = strToBool, help="copy zotero database to local storage")

# main script
if __name__ == "__main__":

    print('\n\n==========================================================')
    start = arrow.get(time.time()).to('US/Pacific').format('YYYY-MM-DD HH:mm:ss ZZ')
    print('Starting at ' + str(start) + '\n\n') 

    # parse the arguments
    args = parser.parse_args()

    # copy the zotero database to the local storage folder
    if args.copyZotero:
        print('Copying zotero database to local storage folder')
        copyFile(constants.READ_ONLY_ZOTERO_DATABASE_PATH, constants.ZOTERO_DATABASE_PATH)
        print('Copying better bibtex database to local storage folder')
        copyFile(constants.READ_ONLY_BETTER_BIBTEX_SEARCH_PATH, constants.BETTER_BIBTEX_SEARCH_PATH)
        print('Done copying')

    # open secrets
    with open(constants.NOTION_SECRET_FILE, "r") as f:
        secrets_notion = json.load(f)

    # initialize notion client and determine notion DB
    notion = Client(auth = secrets_notion['notionToken'])
    notionDB_id = secrets_notion['databaseID']

    # get data from Zotero
    zoteroDataList = getDataFromZoteroDatabases()
    print('Number of items in Zotero: ' + str(len(zoteroDataList)))

    # port data to notion
    print('Starting porting data to notion')
    portZoteroDataToNotion(zoteroDataList, notion, notionDB_id)
    print('Done porting data to notion')

    end = arrow.get(time.time()).to('US/Pacific').format('YYYY-MM-DD HH:mm:ss ZZ')
    print('\n\n' + 'Ending at ' + str(end)) 
    print('==========================================================\n\n')