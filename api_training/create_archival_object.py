from archivesspace import archivesspace
import argparse
import json
import logging
import csv


# This is code to create a simple archival object in ArchivesSpace
# ------------------------------------------------

# Lines 14-24 read the server specified in archivesspace.cfg and connect to it
if __name__ == "__main__":

    CONFIGFILE = "archivesspace.cfg"

    argparser = argparse.ArgumentParser()
    argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
    cliArguments = argparser.parse_args()

    aspace = archivesspace.ArchivesSpace()
    aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
    aspace.connect()

    logging.basicConfig(level=logging.INFO)


    # Name of the csv file. Here it is saved as a variable. 
    csv_file = 'make_ao_data.csv'

    # Python's way of opening and reading CSV files 
    with open(csv_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile) # Reading the file as a key/value dictionary
       
        # Iterate over each row in the spreadsheet
        for row in reader:
            # To see the keys (i.e., column headings in a spreadsheet, print out row.keys())
            title = row['\ufefftitle'] 
            # As you can see here, unlike in the spreadsheet, 'title' is encoded with non-ASCII chars, which is why it looks like this
            level = row['level'].lower() 
            ''' Controlled value fields, like level, are case-sensitive. 
            Use lower() to make sure that the value is lowercase, just as a precaution. 
            Otherwise an error will be thrown when trying to post '''
            resource_uri = row['resource_uri']

            # This is the basic data structure for creating an archival object 
            archival_object_dict = {"jsonmodel_type":"archival_object",
            "external_ids":[],
            "subjects":[],
            "linked_events":[],
            "extents":[],
            "dates":[],
            "external_documents":[],
            "rights_statements":[],
        	"linked_agents":[],
        	"is_slug_auto": True,
        	"restrictions_apply": False,
        	"publish": True,
        	"ancestors":[],
        	"instances":[], 
        	"notes":[],
        	"level": level, # Required field, controlled value
        	"component_id": "",
        	"title": title, # Required field
        	"resource": {"ref": resource_uri}} # Required field

            ''' Post the archival object, passing the first part of the archival object uri and
             the archival object data structure as arguments to aspace.post() '''
            post_archival_object = aspace.post('/repositories/2/archival_objects', archival_object_dict)
            print(post_archival_object)

            ''' If correctly posted, you will see a message on the command line like this for each object created:
            {'status': 'Created', 'id': 248522, 'lock_version': 0, 'stale': True, 'uri': '/repositories/2/archival_objects/248522', 'warnings': []} '''


