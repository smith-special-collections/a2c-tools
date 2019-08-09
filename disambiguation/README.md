Code to disambiguate top containers in ArchivesSpace. This code assumes that the first series in the collection has the correct top containers linked to its archival objects and that successive series in the collection need to be disambiguated. Folder and file order is preserved, while dummy top containers with fake barcodes are created.

In order to run, the follow arguments are passed to the command line:
- archivesspace config
- repo number
- resource number

Tested on Python 3.7.4.
