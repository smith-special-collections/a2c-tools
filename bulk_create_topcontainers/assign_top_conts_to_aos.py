from archivesspace import archivesspace
import argparse
import logging
import csv


def create_top_container_instance(ao_record, top_container_uri):
	'''Function to create top container instance of specified top container
	 for specfied archival object'''
	instance = {'instance_type': 'mixed_materials',
                'is_representative': False,
                'jsonmodel_type': 'instance',
                'sub_container': {'jsonmodel_type': 'sub_container',
                                  'top_container': {'ref': top_container_uri}
                                  }}
    
	ao_record['instances'].append(instance)
                            
	return ao_record


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVname", default="DEFAULT", help="Name of the CSV spreadsheet, e.g, 'bulk_container_spreadsheet.csv. Note: It must be in the same directory as this code file.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)


	with open(cliArguments.CSVname, 'r') as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			try:
				ao_record = aspace.get(row['ao_uri'])
				try:
					create_top_container_instance(ao_record, row['top_cont_uri'])
					post = aspace.post(ao_record['uri'], ao_record)
					logging.info('Archival object successfully linked to top container: {}'.format(ao_record['uri']))
				except Exception as e:
					logging.error(e)
					pass				
			except Exception as e:
				logging.error(e)
				pass
			

