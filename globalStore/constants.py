"""
Author: Nandita Bhaskhar
All global constants
"""

import os
import sys
sys.path.append('../')
import json

NOTION_SECRET_FILE = "../secrets/secrets_notion.json"
ZOTERO_SECRET_FILE = "../secrets/secrets_zotero.json"

with open(ZOTERO_SECRET_FILE, 'r') as f:
    zotero_secrets = json.load(f)

DATA_DIR = zotero_secrets['zotero_local_copy_folderpath']
READ_ONLY_DATA_DIR = zotero_secrets['zotero_local_main_folderpath']

READ_ONLY_ZOTERO_DATABASE_PATH = os.path.join(READ_ONLY_DATA_DIR, "zotero.sqlite")
ZOTERO_DATABASE_PATH = os.path.join(DATA_DIR, "zotero.sqlite")

READ_ONLY_BETTER_BIBTEX_SEARCH_PATH = os.path.join(READ_ONLY_DATA_DIR, "better-bibtex-search.sqlite")
BETTER_BIBTEX_SEARCH_PATH = os.path.join(DATA_DIR, "better-bibtex-search.sqlite")



