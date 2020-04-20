Tested on ArchivesSpace 2.7.1 and Python 3.7.8.

These scripts match and replace Smith's subjects with Library of Congress subject data, correcting title and authority id differences and adding LoC uris to our ArchivesSpace subject records.

database_connect.py requires a Postgre SQL database populated with LoC subject data to match 1:1 Smith subjects to LoC subjects.
