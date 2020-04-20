Tested on ArchivesSpace 2.7.1 and Python 3.7.8.

These scripts are intended to clean up Smith College Special Collection's subject data. Objectives of this cleanup are to remove erroneous subdivisions and to match and reconcile our subjects with Library of Congress subject data (title, authority id, Library of Congress subject uri). Our ArchivesSpace subject records are updated accordingly. 


remove_bad_subdivisions.py runs over a JSON file of subjects identified via a SQL query as having erroneous subdivisions (History, Biography, Sources) and then removes from the title of the ArchivesSpace subject record. Since this will result in subjects with duplicate names (e.g., the subject Women -- History -- Sources, with subdivisions removed, will clash with the subject Women), a temporary id is assigned to these subjects, which will later be removed.

delete_dupes.py deletes duplicates caused by removing bad subdivisions, choosing as its victim the duplicate subject with the temporary id. It merges the dupes and gives all linked records to the survivor.

database_connect.py requires a Postgre SQL database populated with LoC subject data to match 1:1 Smith subjects to LoC subjects.
