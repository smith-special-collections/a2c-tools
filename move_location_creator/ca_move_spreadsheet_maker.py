from pprint import pprint as pp
from asnake.aspace import ASpace
import logging
import csv
import argparse
import re
from datetime import datetime

## NOTE: If using on local instance, MUST create 'volume' as valid container type
START_DATE = datetime.today().strftime('%Y-%m-%d')

# def make_location_mapping_object(location_mapping_file):
# 	column_ids = []
# 	uris = []	
# 	with open(location_mapping_file) as csv_file:
# 		reader = csv.DictReader(csv_file)
# 		for row in reader:
# 			for k in row.keys():
# 				if 'URI' in k:
# 					if row[k] != '':
# 						id_ = row[k].split('/')[-1]
# 						uris.append(id_)

# 	location_object = []					
# 	chunks = chunk_ids(uris)
# 	for chunk in chunks:
# 		locations = aspace.client.get(f'/locations?id_set={chunk}')
# 		for location_data in locations.json():
# 			location_dict = {}
# 			location_dict[location_data['title']] = location_data['uri']
# 			location_object.append(location_dict)

# 	location_object = [dict(t) for t in {tuple(d.items()) for d in location_object}]
# 	return location_object


def make_location_mapping_object(location_mapping_file):
	column_ids = []
	rows = []	
	with open(location_mapping_file) as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			for k in row.keys():
				if row[k] != '':
					tup = (k, row[k])
					rows.append(tup)				

	all_ds = []
	count = len(rows)
	while count > 0:
		count += -2
		d = {}
		v = rows[-1][1].replace('https://archivesspace.smith.edu', '')
		d[rows[-2][1]] = v		
		all_ds.append(d)
		del rows[-1]
		del rows[-1]

	location_object = [dict(t) for t in {tuple(d.items()) for d in all_ds}]
	return location_object


def chunk_ids(id_list):
	ids = []
	if len(id_list) > 25:
		id_chunks = [id_list[uri:uri + 25] for uri in range(0, len(id_list), 25)]
		for chunk in id_chunks:
			chunk = [str(i) for i in chunk]
			chunk = ','.join(chunk)
			ids.append(chunk)
	else:
		id_list = [str(i) for i in id_list]
		id_list = ','.join(id_list)
		ids.append(id_list)

	return ids


def group_top_containers(csv_dict):
	top_containers = []
	tc_1 = {key : val for key, val in csv_dict.items() if '1' in key}
	tc_2 = {key : val for key, val in csv_dict.items() if '2' in key}
	tc_3 = {key : val for key, val in csv_dict.items() if '3' in key}

	top_containers.append(tc_1)
	top_containers.append(tc_2)
	top_containers.append(tc_3)

	return top_containers


def top_container_schema():
	top_container = {'active_restrictions': [],
	 'barcode': '',
	 'collection': [],
	 'container_locations': [{'jsonmodel_type': 'container_location',
	                          'ref': '',
	                          'status': 'current',
	                          'start_date': START_DATE}],
	 'container_profile': {'ref': '/container_profiles/78'},
	 'indicator': '',
	 'jsonmodel_type': 'top_container',
	 'repository': {'ref': '/repositories/4'},
	 'restricted': False,
	 'type': 'volume'}

	return top_container


def map_container_locations(location_mapping_object, grouped_top_containers):
	location = None
	top_container_schemas = []
	for grouping in grouped_top_containers:
		for k, v in grouping.items():
			if 'location' in k:
				if v != '':
					location = v
			if 'barcode' in k:
				if v != '':
					barcode = v
			if 'volume' in k:
				if v != '':
					volume = v

 
		if location != None:
			for location_dict in location_mapping_object:
				if location in location_dict.keys():
					location = location_dict[location]
					schema = top_container_schema()
					schema['container_locations'][0]['ref'] = location
					schema['barcode'] = barcode
					schema['indicator'] = volume
					top_container_schemas.append(schema)


	return top_container_schemas


def post_top_containers(schemas):
	post_uris = []
	for schema in schemas:
		try:
			post = aspace.client.post('/repositories/4/top_containers', json=schema).json()
		# pp(post)
			logging.info(f'Top container created: {post["uri"]}')
			post_uris.append(post['uri'])
		except Exception as e:
			logging.error(f'Top container {schema["barcode"]} could not be made: {e}')

	return post_uris


def create_top_container_instances(top_container_uris):
	instances = []
	for uri in top_container_uris:
		instance = {'instance_type': 'mixed_materials',
	                'is_representative': False,
	                'jsonmodel_type': 'instance',
	                'sub_container': {'jsonmodel_type': 'sub_container',
	                                  'top_container': {'ref': uri}}}
		instances.append(instance)

	return instances


def make_date_subrecord(csv_dict):

	date = {}

	if csv_dict['date_begin'] != '' and csv_dict['date_end'] != '':
		date['begin'] = csv_dict['date_begin']
		date['end'] = csv_dict['date_end']
		date['date_type'] = 'inclusive'
		date['jsonmodel_type'] = 'date'
		date['label'] = 'creation'
		# date['calendar'] = 'gregorian'
		# date['era'] = 'ce'
		return date

	if csv_dict['date_begin'] != '' and csv_dict['date_end'] == '':
		date['begin'] = csv_dict['date_begin']
		date['date_type'] = 'single'
		date['jsonmodel_type'] = 'date'
		date['label'] = 'creation'
		# date['calendar'] = 'gregorian'
		# date['era'] = 'ce'
		return date

	if csv_dict['date_begin'] == '' and csv_dict['date_end'] != '':
		logging.error(f'Date end but no date begin for object {csv_dict["title"]}')	
		return None

	if csv_dict['date_begin'] == '' and csv_dict['date_end'] == '':
		return None


def create_archival_object_schema(csv_dict, top_container_instances):
	'''Function to create an archival object based on data from the spreadsheet'''
	record_schema = {
		"jsonmodel_type": "archival_object",
		"external_ids": [],
		"subjects": [],
		"linked_events": [],
		"extents": [],
		"lang_materials": [],
		"dates": [],
		"external_documents": [],
		"rights_statements": [],
		"linked_agents": [],
		"is_slug_auto": True,
		"publish": True,
		"restrictions_apply": False,
		"ancestors": [],
		"instances": [],
		"notes": [],
		"level": "file",
		"title": csv_dict['title'],
		"resource":{ "ref": csv_dict['resource_uri']}
	}

	date = make_date_subrecord(csv_dict)
	if date != None:
		record_schema['dates'].append(date)

	for instance in top_container_instances:
		record_schema['instances'].append(instance)

	return record_schema
	

def post_archival_object(csv_dict, location_mapping_object): # row
	grouped_top_containers = group_top_containers(csv_dict)
	top_container_schemas = map_container_locations(location_mapping_object, grouped_top_containers)
	top_container_uris = post_top_containers(top_container_schemas)
	pp(top_container_uris)
	top_container_instances = create_top_container_instances(top_container_uris)
	archival_object_schema = create_archival_object_schema(csv_dict, top_container_instances)

	try:
		post = aspace.client.post('/repositories/4/archival_objects', json=archival_object_schema).json()
		logging.info(f'Archival object {csv_dict["title"]} created')
		pp(post['uri'])
	except Exception as e:
		logging.error(f'Archival object {csv_dict["title"]} failed: {e}')


if __name__ == "__main__":


	argparser = argparse.ArgumentParser(description="Create CA archival objects and top containers")
	argparser.add_argument("CSV_FILE", help="CSV file of archival object data to be created")
	argparser.add_argument("LOCATION_MAPPING_FILE", help="CSV file of location mappings")
	cliargs = argparser.parse_args()

	aspace = ASpace()

	logging.basicConfig(level=logging.INFO)

	location_mapping_file = cliargs.LOCATION_MAPPING_FILE
	location_mapping_object = make_location_mapping_object(location_mapping_file)
	# pp(location_mapping_object)

	with open(cliargs.CSV_FILE, encoding='utf-8-sig') as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader: 
			post_archival_object(row, location_mapping_object)
			# grouped_top_containers = group_top_containers(row)
			# top_container_schemas = map_container_locations(location_mapping_object, grouped_top_containers)
			# # pp(top_container_schemas)
			# top_container_uris = post_top_containers(top_container_schemas)
			# pp(top_container_uris)



