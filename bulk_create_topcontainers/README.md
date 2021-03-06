Tested on Python 3.7.4 and ArchivesSpace v2.6.0.

bulk_create_containers.py is code to bulk create top containers and link them to bulk created series-level archival objects from a spreadsheet. 

When run, the script creates accessions as series level archival objects and then creates top containers for those objects, according to information provided in the spreadsheet (see: template) and links them together as instances of the object. The name of the spreadsheet is passed as an argument on the command line. Requires archivesspace module (https://github.com/SmithCollegeLibraries/archivesspace-python) to run.

``` python3 bulk_create_containers.py local bulk_container_spreadsheet.csv ```


assign_top_conts_to_aos.py is code to link specified preexisting top containers to specified archival objects. It pulls the data from a spreadsheet like sample_ao_conts_uris.csv to make the link. The name of the spreadsheet is a command line argument.

```python3 assign_top_conts_to_aos.py local sample_ao_conts_uris.csv```
