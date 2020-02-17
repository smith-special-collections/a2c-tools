from archivesspace import archivesspace
from os import listdir
from os.path import isfile, join
import os
import pprint
import argparse
import logging
import json


def extract_folder_name(subfolder):
	folder = subfolder.split('/')[-1]
		
	return folder


def join_resource_ids(resource_record):	
	dash = '-'
	ids = []
	if len(resource_record['id_0']) != 0 and len(resource_record['id_1']) != 0 and len(resource_record['id_2']) != 0:
		ids.append(resource_record['id_0'])
		ids.append(resource_record['id_1'])
		ids.append(resource_record['id_2'])
	full_id = dash.join(ids)
	
	return full_id


def findKey(d, key):
    """Find all instances of key."""
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j


def string_to_list(string):
	''' 
	Transform this '["SSC", '"MS", '"00806", null]'
	to this ['SSC', 'MS', '00806']
	'''
	string = string[1:-1]
	string = string.replace('"', "")
	string = string.split(',')
	string.pop()

	return string


def make_full_accession_id(l):
	''' 
	Transform this ['SSC', 'MS', '00806']
	to this 'SSC-MS-00806'
	'''
	dash = '-'
	l = dash.join(l)

	return l


def make_match(subfolders, resources):
	# Pulling out folder name
	dirs = []
	for subfolder in subfolders:
		dir_info = {}
		folder_name = extract_folder_name(subfolder)
		dir_info['directory'] = folder_name
		# Pulling out file names and putting them into a list
		dir_info['files'] = [f for f in listdir(subfolder) if isfile(join(subfolder, f))]
		for rec in resources['RECORDS']:
			try:
				resource_id = make_full_accession_id(string_to_list(rec['accession_id']))
				if resource_id != None:
					if resource_id == folder_name:
						# Pulling out matching resource uri of directory name
						dir_info['resource_uri'] = rec['uri']
						endpoint = rec['uri'] + '/tree'
						output = aspace.get(endpoint)
						# Getting children uris 
						dir_info['resource_children'] = [value for value in findKey(output, 'record_uri') if value != None]
			except:
				logging.warning('Record not found: {}'.format(rec['uri']))
				pass

		dirs.append(dir_info)
	
	return dirs


def strip_component_id(aspace_rec):
	if 'component_id' in aspace_rec.keys():
		if 'Accession' in aspace_rec['component_id']:
			aspace_rec['component_id'] = aspace_rec['component_id'].split('Accession')[1].strip()

	return aspace_rec


def add_file_note(aspace_record, file_path):
	new_note =  {'jsonmodel_type': 'note_multipart',
	  'publish': True,
	  'subnotes': [{'content': 'For a preliminary content listing, please see the PDF <a href=' + file_path + '>inventory to Accession {}.</a>'.format(file_path.split('/')[-1][:-4]),
	                'jsonmodel_type': 'note_text',
	                'publish': True}],
	  'type': 'otherfindaid'}
	
	aspace_record['notes'].append(new_note)

	return aspace_record


def add_resource_note(resource):
	new_note =  {'jsonmodel_type': 'note_multipart',
	  'publish': True,
	  'subnotes': [{'content': 'One or more inventories made at the time of accessioning are available as PDFs. Links can be found in the description of the individual accessions.',
	                'jsonmodel_type': 'note_text',
	                'publish': True}],
	  'type': 'otherfindaid'}
	
	resource['notes'].append(new_note)

	return resource


def check_resource_for_note(resource):
	string = 'One or more inventories made at the time of accessioning are available as PDFs. Links can be found in the description of the individual accessions.'
	check = 0
	for note in resource['notes']:
		if 'subnotes' in note.keys():
			for subnote in note['subnotes']:
				try:
					if subnote['content'] == string:
						check += 1
				except:
					pass
	if check == 0:
		aspace.post(resource['uri'], add_resource_note(resource))
		logging.info('Other finding aid note added to Resource {}'.format(resource['title']))
	else:
		logging.warning('Resource {} already has other finding aid note'.format(resource['title']))


def check_ao_for_note(ao, file_path): # This is for a singular archival object, don't append to list 
	check = 0
	for note in ao['notes']:
		if 'subnotes' in note.keys():
			for subnote in note['subnotes']:
				try:
					if file_path in subnote['content']:
						check += 1
				except:
					pass
	if check == 0:
		try:
			aspace.post(ao['uri'], add_file_note(ao, file_path))
			logging.info('Other finding aid note added to Archival Object {}'.format(ao['title']))
		except:
			logging.warning('Unable to update Archival Object {}'.format(ao['title']))
			return ao['uri']
	else:
		logging.warning('Archival Object {} already has other finding aid note'.format(ao['title']))

	
def update_record(match): 
	successful_files = []
	for uri in match['resource_children']:
		try:
			rec = strip_component_id(aspace.get(uri))
			for file in match['files']:
				if file.split('.')[0] == rec['component_id']:					
					file_path = 'http://libtest.smith.edu/accessions/' + match['directory'] + '/' + file
					try:
						# post = aspace.post(rec['uri'], add_file_note(rec, file_path))
						check_ao_for_note(rec, file_path) # Also posts
						successful_files.append(file)
					except:
						pass
		except:
			pass

	# Checking to see what files did not get linked
	unmatched = []
	for f in match['files']:
		if f in successful_files:
			pass
		else:
			unmatched.append(f)

	if len(unmatched) > 0:
		return unmatched


def update_resource_with_note(match):
	for uri in match['resource_children']:
		if 'resource' in uri:
			resource = uri
			rec = aspace.get(resource)
			check_resource_for_note(rec)


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"
	
	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("FILE_PATH", default="DEFAULT", help="URI")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	mypath = cliArguments.FILE_PATH

	subfolders = [f.path for f in os.scandir(mypath) if f.is_dir()]

	with open('resource_accession_nums.json') as json_file:
		try:
			resources = json.load(json_file)
		except ValueError:
			logging.warning('File not found')
			exit()


	# Initializing dictionary for data storage
	data = {}
	data['rows'] = []
	
	# Making resource/archival object matches
	data['rows'].extend(make_match(subfolders, resources))
	logging.info('Matches made!')

	# Writing to JSON file	
	with open('file_matches.txt', 'w') as outfile:
		json.dump(data, outfile)

	# Attaching notes and updating ASpace records
	with open('file_matches.txt') as json_file:
		try:
			matches = json.load(json_file)
		except:
			logging.warning('File not found')
			exit()

	data = {}
	data['rows'] = []
	for match in matches['rows']:
		try:
			file_update = update_record(match)
			if file_update != None:
				d = {}
				d['directory'] = match['directory']
				d['resource_uri'] = match['resource_uri']
				d['misses'] = file_update # List of unmatched files
				data['rows'].append(d)
		except:
			pass
		try:
			resource_update = update_resource_with_note(match)
		except:
			pass

	
	with open('unlinked_pdfs.txt', 'w') as outfile:
		json.dump(data, outfile)
		

	logging.info('All done!')

	










