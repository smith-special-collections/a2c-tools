from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import pandas as pd
import os


def load_json_source(json_file_name): 
	''' Function to open file and return file contents '''
	file_contents = []
	with open(json_file_name) as json_file:
		try:
			objects = json.load(json_file)
		except ValueError:
			logging.info('File not found.')
	
	for obj in objects:
		file_contents.append(obj)

	return file_contents


def add_repo_num_and_accession_uri_keys_to_json_contents(json_contents):
	''' Adding keys to JSON contents that will hold values produced later in the script '''
	for content in json_contents:
		content['accession_uri'] = ''
		content['repo_num'] = content['collection_uri'].split('/')[2] 

	return json_contents


def extract_unique_accession_ids(json_contents):
	''' Function to pull out unique accession ids and resource uris for creation of series archival objects '''
	unique_accession_ids = []
	for content in json_contents:
		if not content['accession_id'] in unique_accession_ids:
			unique_accession_ids.append(content['accession_id'])

	return unique_accession_ids


def make_tuples_for_accession_creation(json_contents, unique_ids):
	''' Function to make tuples with necessary data for series level archival object creation '''
	accession_tuples = []
	for i in unique_ids:
		for content in json_contents:
			if i == content['accession_id']:
				tup = (i, content['collection_uri'], content['repo_num'], content['level_of_description'].lower())
				if not tup in accession_tuples:
					accession_tuples.append(tup)

	return accession_tuples 


def create_box(top_container):
	'''Function to create a new top container'''
	container_dict = {'active_restrictions': [],
		'collection': [],
		'container_locations': [],
		'container_profile': {},
		'indicator': str(top_container['container_indicator']),
		'jsonmodel_type': 'top_container',
		'repository': {'ref': '/repositories/' + str(top_container['repo_num'])},
		'restricted': False,
		'series': [],
		'type':'box',
		'publish': True}

	post = aspace.post('/repositories/' + str(top_container['repo_num']) + '/top_containers', container_dict)

	return post['uri']


def create_archival_object(accession_tuple):
	'''Function to create a series level archival object'''
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
		"level": accession_tuple[3],
		"component_id": "Accession " + accession_tuple[0],
		"title": "Accession " + accession_tuple[0],
		"resource": { "ref": accession_tuple[1]}}

	post_archival_object = aspace.post('/repositories/' + str(accession_tuple[2]) + '/archival_objects', archival_object_dict)

	return post_archival_object['uri']


def make_archival_objects_and_put_uris_into_json_contents(json_contents, tuples):
	''' Function to make the archival object from accession tuples and then insert the new uri into JSON contents '''
	accession_tuples = []
	for tup in tuples:
		try:
			series = create_archival_object(tup)
			logging.info('New series level archival object created: {}'.format(series))
			series_tup = (series, tup[0])
			accession_tuples.append(series_tup)
		except Exception as e:
			logging.warning('Failed to create new series level archival object for Accession {}. {}'.format(series_tup[0], e))
			pass

	for content in json_contents:
		for tup in accession_tuples:
			if content['accession_id'] == tup[1]:
				content['accession_uri'] = tup[0]


def create_boxes_and_link_them_to_accessions(json_contents):
	''' Function to create new boxes and linked them to the appropriate newly created series level archival record '''
	for content in json_contents:
		try:
			box = create_box(content)
			logging.info('Creating top container {} for Accession {}'.format(content['container_indicator'], content['accession_id']))
			instance = {'instance_type': content['instance_type'].lower(),
	                'is_representative': False,
	                'jsonmodel_type': 'instance',
	                'sub_container': {'jsonmodel_type': 'sub_container',
	                                  'top_container': {'ref': box},},}
			accession = aspace.get(content['accession_uri'])
			accession['instances'].append(instance)
			post = aspace.post(accession['uri'], accession)
			logging.debug(post)
		except Exception as e:
			logging.warning('Failed to create or link new containers to Accession {}'.format(content['accession_id'])) 
			pass


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

	file_name = cliArguments.CSVname


	# Reads CSV file
	csv_file = pd.DataFrame(pd.read_csv(file_name, sep = ",", header = 0, index_col = False))
	
	# Creates new JSON file name
	csv_split = file_name.split('.')
	json_file = csv_split[0] + ".json"

	# Transforms CSV into JSON for parsing
	csv_file.to_json(json_file, orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

	# Opening JSON file 
	json_contents = load_json_source(json_file)	

	# Creating new series level archival object records for accessions data and linking newly created top containers to them
	add_repo_num_and_accession_uri_keys_to_json_contents(json_contents)
	unique_ids = extract_unique_accession_ids(json_contents)
	tuples = make_tuples_for_accession_creation(json_contents, unique_ids)
	make_archival_objects_and_put_uris_into_json_contents(json_contents, tuples)
	create_boxes_and_link_them_to_accessions(json_contents)                   	

	# Deleting JSON file as no longer of any use
	os.system('rm ' + json_file)


