from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import pandas as pd


def create_box(top_container):
	'''Function to create a new top container'''
	
	repo_num = top_container['collection_uri'].split('/')[2]	
	container_dict = {'active_restrictions': [],
		'collection': [],
		'container_locations': [],
		'container_profile': {},
		'indicator': str(top_container['container_indicator']),
		'jsonmodel_type': 'top_container',
		'repository': {'ref': '/repositories/' + str(repo_num)},
		'restricted': False,
		'series': [],
		'type':'box',
		'publish': True}

	post_top_container = aspace.post('/repositories/' + str(repo_num) + '/top_containers', container_dict)

	return post_top_container['uri']


def create_archival_object(accession_tuple):
	'''Function to create a series level archival object'''

	repo_num = accession_tuple[1].split('/')[2]
	archival_object_dict = { "jsonmodel_type":"archival_object",
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
		"level": "series",
		"component_id": "Accession " + accession_tuple[0],
		"title": "Accession " + accession_tuple[0],
		"resource": { "ref": accession_tuple[1]}}

	post_archival_object = aspace.post('/repositories/' + str(repo_num) + '/archival_objects', archival_object_dict)

	return post_archival_object['uri']


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVname", nargs="?", default="DEFAULT", help="Name of the CSV spreadsheet, e.g, 'bulk_container_spreadsheet.csv. Note: It must be in the same directory as this code file.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	file = cliArguments.CSVname


	# Reads CSV file
	csv_file = pd.DataFrame(pd.read_csv(file, sep = ",", header = 0, index_col = False))
	
	# Creates new JSON file name
	csv_split = file.split('.')
	json_file = csv_split[0] + ".json"

	
	# Transforms CSV into JSON for parsing
	csv_file.to_json(json_file, orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

	
	# Opens JSON file
	with open(json_file) as jsonfile:
		try:
			top_containers = json.load(jsonfile)
		except ValueError:
			logging.info('File not found')
			exit(1)

	
	# Pulling out unique accession ids and resource uris for creation of series archival objects
	uniq_accession_ids = []
	for top_cont in top_containers:
		if not top_cont['accession_id'] in uniq_accession_ids:
			uniq_accession_ids.append(top_cont['accession_id'])

	
	uniq_accession_tups = []
	for i in uniq_accession_ids:
		for top_cont in top_containers:
			if i == top_cont['accession_id']:
				accession_tup = (i, top_cont['collection_uri'])
				if not accession_tup in uniq_accession_tups:
					uniq_accession_tups.append(accession_tup)
	

	# Creating series level archival objects from accessions information
	new_series_tups = []
	for count, tup in enumerate(uniq_accession_tups, 1):
		print(count)
		try:
			series = create_archival_object(tup)
			logging.info('New series level archival object created: {}'.format(series))
			new_series_tup = (series, tup[0])
			new_series_tups.append(new_series_tup)
		except:
			logging.info('Failed to create new series level archival object for Accession {}'.format(tup[0]))
			pass
	

	# Inserting new accesssion uris back into top_containers
	for top_cont in top_containers:
		for tup in new_series_tups:
			if top_cont['accession_id'] == tup[1]:
				top_cont['accession_uri'] = tup[0]
	
		
	# Creating new accessions and linking them to the accession
	for count, top_cont in enumerate(top_containers, 1):
		print(count)
		try:
			new_top_cont = create_box(top_cont)
			logging.info('Creating top container {} for Accession {}'.format(top_cont['container_indicator'], top_cont['accession_id']))
			instance = {'instance_type': 'mixed_materials',
	                'is_representative': False,
	                'jsonmodel_type': 'instance',
	                'sub_container': {'jsonmodel_type': 'sub_container',
	                                  'top_container': {'ref': new_top_cont},},}
			accession = aspace.get(top_cont['accession_uri'])
			accession['instances'].append(instance)
			post_accession = aspace.post(accession['uri'], accession)
			pprint.pprint(post_accession)
		except:
			logging.info('Failed to create or link new containers to Accession {}'.format(top_cont['accession_id']))
			pass




