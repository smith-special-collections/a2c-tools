import pprint
from archivesspace import archivesspace
import logging
import argparse
import csv
from pprint import pprint as pp

# Generates spreadsheet for label creation


def findKey(d, key):
    """Find all instances of key."""
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j


def get_all_archival_object_uris_for_resource():
	endpoint = '/repositories/' + repo + '/resources/' + resource + '/tree'
	output = aspace.get(endpoint)
	uris = []
	for value in findKey(output, 'record_uri'):
		if 'archival_objects' in value:
			uris.append(value)

	return uris


def get_series(tree):
	for t in tree['children']:
		yield t


def get_unique_top_containers(children_uris):
	instances = []
	for uri in children_uris:
		child = aspace.get(uri)
		if len(child['instances']) != 0:
			if child['instances'][0]['sub_container']['top_container']['ref'] not in instances:
				instances.append(child['instances'][0]['sub_container']['top_container']['ref'])


	return instances


def get_repo_full_name():
	if repo == str(2):
		full_name = 'Sophia Smith Collection'
	elif repo == str(3):
		full_name = 'Mortimer Rare Book Collection'
	elif repo == str(4):
		full_name = 'Smith College Archives'
	else:
		pass

	return full_name


def join_resource_ids(resource_record): 
    '''
    Concantenates individual id fields into single string
    '''
    dash = '-'
    ids = []
    if len(resource_record['id_0']) != 0 and len(resource_record['id_1']) != 0 and len(resource_record['id_2']) != 0:
        ids.append(resource_record['id_0'])
        ids.append(resource_record['id_1'])
        ids.append(resource_record['id_2'])
    full_id = dash.join(ids)
    
    return full_id

	
def get_collection_info():
	resource_record = aspace.get('/repositories/'+repo+'/resources/'+resource)
	resource_title = resource_record['title']
	resource_id = join_resource_ids(resource_record)
		
	id_and_title = (resource_id, resource_title)
	
	return id_and_title


def get_series_info(series_uri):
	series = aspace.get(series_uri)
	try:
		if 'component_id' in series.keys():
			component_id = 'Series ' + series['component_id']
		else:
			component_id = ""
		if 'title' in series.keys():
			title = series['title']
		else:
			title = ""
		tup = (title, component_id)
		return tup
	except KeyError:
		pass
	except Exception as e:
		logging.error(e)


def get_top_container_tups():
	tree = aspace.get('/repositories/'+repo+'/resources/'+resource+'/tree')

	net = []
	top_containers_and_series_uris = []
	for value in get_series(tree):
		series_uris = [v for v in findKey(value, 'record_uri') if v != None]
		series_unique_top_containers = get_unique_top_containers(series_uris)
		for uri in series_unique_top_containers:
			if uri not in net:
				net.append(uri)
				series_and_top_container = (value['record_uri'], uri)
				top_containers_and_series_uris.append(series_and_top_container)

	return top_containers_and_series_uris


def get_label_size(container_profile_uri):
		profile = aspace.get(container_profile_uri)
		num = int(container_profile_uri.split('/')[-1])
		bad_nums = [23, 24, 77, 78, 79]
		if num in bad_nums:
			size = "invalid"
		else:
			if num == 4 or num == 2:
				size = 'half'
			else:
				if int(profile['height']) < int(4.5):
					size = 'oversize'
				else:
					size = 'regular'

		return size


def get_top_container_info(container_uri):
		container_record = aspace.get(container_uri)
		try:
			size = get_label_size(container_record['container_profile']['ref'])
		except:
			size = "invalid"
		if 'shared' in container_record['indicator']:
			ind = ""
		else:
			ind = container_record['indicator']
		if container_record['type'] == 'tube' or container_record['type'] == 'reel' or container_record['type'] == 'box' or container_record['type'] == 'roll':
			typ = container_record['type']
		else:
			typ = 'invalid container type'
		tup = (typ, ind, size)

		return tup


def get_spreadsheet_data():
	top_container_tups = get_top_container_tups() 
	resource_info = get_collection_info()
	repo_name = get_repo_full_name()
	
	top_container_info = {}
	top_container_info['data'] = []
	for tup in top_container_tups:
		d = {}
		container_info = get_top_container_info(tup[1])
		series_info = get_series_info(tup[0])
		d['repo_name'] = repo_name
		d['collection_title'] = resource_info[1]
		d['collection_id'] = resource_info[0]
		if series_info[1] != "":
			d['series_id'] = series_info[1]
			d['series_title'] = series_info[0]
		else:
			d['series_id'] = series_info[1]
			d['series_title'] = ""
		d['container_type'] = container_info[0]
		d['container_indicator'] = container_info[1]
		if container_info[2] != "invalid":
			d['label_size'] = container_info[2]
		else:
			d['label_size'] = 'regular'


		top_container_info['data'].append(d)

	return top_container_info


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("REPO", default="DEFAULT", help="Repository number")
	argparser.add_argument("RESOURCE", nargs="?", default="DEFAULT", help="Resource number")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	repo = cliArguments.REPO
	resource = cliArguments.RESOURCE
	
	# Get top container information
	spreadsheet_info = get_spreadsheet_data()

	regular = {}
	regular['data'] = []

	half = {}
	half['data'] = []

	oversize = {}
	oversize['data'] = []


	for row in spreadsheet_info['data']:
		if row['label_size'] == 'regular':
			regular['data'].append(row)
		elif row['label_size'] == 'half':
			half['data'].append(row)
		elif row['label_size'] == 'oversize':
			oversize['data'].append(row)

	# Make spreadsheets
	keys = spreadsheet_info['data'][0].keys()
	
	reg_outpath = 'reg_labels_for_resource_' + spreadsheet_info['data'][0]['collection_title'].replace(" ", "_") + '.csv'
	half_outpath = 'half_labels_for_resource_' + spreadsheet_info['data'][0]['collection_title'].replace(" ", "_") + '.csv'
	os_outpath = 'os_labels_for_resource_' + spreadsheet_info['data'][0]['collection_title'].replace(" ", "_") + '.csv'
	

	if len(regular['data']) > 0:
		with open(reg_outpath, 'w') as f:
			w = csv.DictWriter(f, keys)
			w.writeheader()
			for obj in regular['data']:
				w.writerow(obj)
			logging.info(f'Spreadsheet generated: {reg_outpath}')

	if len(half['data']) > 0:
		with open(half_outpath, 'w') as f:
			w = csv.DictWriter(f, keys)
			w.writeheader()
			for obj in half['data']:
				w.writerow(obj)
		logging.info(f'Spreadsheet generated: {half_outpath}')

	if len(oversize['data']) > 0:
		with open(os_outpath, 'w') as f:
			w = csv.DictWriter(f, keys)
			w.writeheader()
			for obj in oversize['data']:
				w.writerow(obj)
		logging.info(f'Spreadsheet generated: {os_outpath}')

	
	
