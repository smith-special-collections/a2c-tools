Tested on Python3.7.4 and requires ArchivesSpace module to run.

do_csv_maker.py takes a repository number and resource number as required inputs and prints out onto the console the most recent series created for the specified resource. If these series are correct, the user types 'y' (or 'n' if they are not) and a CSV file is created containing information pertaining only to the archival objects for those series. The CSV file will then be filled in with pertinent digital object data by the digital archivist for use in another script, as yet to be written.

The generated CSV is called digital_object_template.csv.

```python3 do_csv_maker.py local 2 751``` 

do_file_version.py takes the name (or path) of a CSV as required input and creates from the CSV data digital objects and links them to archival objects.  

```python3 do_file_version.py local digital_object_template.csv```
