<div align="center">    
 
# Zotero To Notion     
  
</div>
 
## Description   
This project allows you to export newly added or recently updated documents in Zotero (local database, synced via Google Drive) to your Notion database via the Notion APIs and by reading the `zotero.sqlite` database LOCALLY. If you'd like the export to happen as soon as you make a change in Zotero, then you can run the script `scripts/runZoteroToNotion.sh` peridocially at a reasonable frequency via a `crontab` job. 

## Directory Structure

```
.
+-- globalStore/
|   +-- constants.py
+-- lib/
|   +-- port_utils.py
|   +-- utils.py
+-- notebooks/
|   +-- Trial_ZoteroDatabase.py
+-- scripts/
|   +-- runZoteroToNotion.sh
+-- secrets/
|   +-- secrets_notion.json
|   +-- secrets_zotero.json
+-- src/
|   +-- zoteroToNotion.py
+-- tests/
|   +-- testNotionAPI.py
|   +-- testZoteroRead.py
+-- .gitignore
+-- juyptext.toml
+-- LICENSE
+-- README.md
+-- requirements.txt
+-- STDOUTlog_examples.txt
```

## Usage
1. Create a python conda env using `requirements.txt`
2. Make sure your local Zotero database is synced to an accessible path via Google Drive (READ_ONLY_DIRECTORY). Ensure that the plugins `BetterBib` and `Zotfile` are installed.
3. Register a private integration on your Notion workspace (follow instructions online)
4. Obtain its `notionToken`
5. Create a database on Notion to contain all the entries from Zotero. Make sure it has the following properties. If you want to add more properties or remove, modify the function `getDataFromZoteroDatabases` and `getNotionPageEntryFromPropObj` in `lib/port_utils.py`.
```
Title property: Citation
Text properties: Title, UID, Authors, Venue, Year, Abstract, Type, BibTex, Filename, CollectionNames, Zotero Tags
Url properties: URL
Date properties: Created At, Last Modified At
```
6. Get its `databaseID` and add it to `secrets/secrets_notion.json` in the following format:
```
{
    "notionToken": "your notion token",
    "databaseID": "your notion database ID"
}
```
7. Run the python script `src/zoteroToNotion.py` with `--copyZotero` argument as True (default)
8. You can periodically run this file again as a script `scripts/runZoteroToNotion.sh` using a crontab job to get periodic updates

## Sources

- [Notion API Python SDK](https://github.com/ramnes/notion-sdk-py)

## If you use it in your work and want to adapt this code, please consider starring this repo or forking from it!

```
@misc{nanbhas2022_zoteroToNotion,
  title={Zotero To Notion},
  author={Nandita Bhaskhar},
  journal={GitHub Repo, https://github.com/nanbhas/ZoteroToNotion},
  year={2022}
}
```  
 

