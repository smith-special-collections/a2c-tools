from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import re
import pandas as pd


def addZeros(id_num):
	'''Function to add leading zeros to id_3'''

	while len(str(id_num)) < 5:
		zero = '0'
		id_num += zero + id_num

	return id_num


def make_note_dict(key, resource):
	'''Function to create note_dicts'''
	
	if key == 'scope_and_con_note_1' or key == 'scope_and_con_note_2' or key == 'scope_and_con_note_3' or key == 'scope_and_con_note_3.1':
		typ = 'scopecontent'
	if key == 'rel_mat_note':
		typ = 'relatedmaterial'
	if key == 'biohist_note_1' or key == 'biohist_note_2':
		typ = 'bioghist'
	if key == 'acq_note_1' or key == 'acq_note_2':
		typ = 'acqinfo'
	if key == 'gen_note_1' or key == 'gen_note_2' or key == 'gen_note_3' or key == 'gen_note_4':
		typ = 'odd'
	if key == 'arrange_note':
		typ = 'arrangement'
	if key == 'con_gov_acc_note':
		typ = 'accessrestrict'
	if key == 'other_fa_note':
		typ = 'otherfindaid'

	if resource[key] != "":
		if key == 'lang_mat_note':
			note = {}
			note['jsonmodel_type'] = 'note_singlepart'
			note['type'] = 'langmaterial'
			note['publish'] = True
			note['content'] = []
			note['content'].append(resource[key])
		else:
			note = {}
			note['jsonmodel_type'] = 'note_multipart'
			note['publish'] = True
			note['type'] = typ
			note['subnotes'] = []
			content = {}
			content['content'] = resource[key]
			content['jsonmodel_type'] = 'note_text'
			content['publish'] = True
			note['subnotes'].append(content)

		return note


def make_resource(resource):
	'''Function to generate MRBC resource record'''
	
	resource_dict = {}
	
	# Dates section
	resource_dict['dates'] = []
	date_dict = {}
	date_dict['jsonmodel_type'] = 'date'
	date_dict['label'] = 'creation'
	if resource['date_begin'] != "":
		date_dict['begin'] = str(int(resource['date_begin']))
		date_dict['calendar'] = 'gregorian'
	if resource['date_end'] != "":
		date_dict['end'] = str(int(resource['date_end']))
	if resource['date_exp'] != "":
		date_dict['expression'] = str(resource['date_exp'])
	if resource['date_type'] != "":
		date_dict['date_type'] = str(resource['date_type'].lower())
	if resource['date_certainty'] != "":
		date_dict['certainty'] = resource['date_certainty'].lower()
	if len(date_dict.keys()) > 2:
		resource_dict['dates'].append(date_dict)

	# Language
	resource_dict['language'] = 'eng'

	# Level
	resource_dict['level'] = 'collection'

	# Title
	resource_dict['title'] = resource['title']

	# Publish
	resource_dict['publish'] = False

	# Subjects
	resource_dict['subjects'] = []

	sub_keys = []
	for key in resource.keys():
		if re.findall('geo', key) or re.findall('genform', key) or re.findall('top', key) or re.findall('un_title', key):
			if key not in sub_keys:
				sub_keys.append(key)

	for key in sub_keys:
		if resource[key] != "":
			sub = {'ref': resource[key]}
			resource_dict['subjects'].append(sub)

	# Agents
	resource_dict['linked_agents'] = []

	ag_keys = []
	for key in resource.keys():
		if re.findall('person', key) or re.findall('family', key) or re.findall('corp_body', key):
			if key not in ag_keys:
				ag_keys.append(key)

	for key in ag_keys:
		if re.findall('creator', key):
			if resource[key] != "":
				agent = {}
				agent['ref'] = resource[key]
				agent['role'] = 'creator'
				agent['terms'] = []
				resource['linked_agents'].append(agent)
		else:
			if resource[key] != "":
				agent = {}
				agent['ref'] = resource[key]
				agent['role'] = 'subject'
				agent['terms'] = []
				resource_dict['linked_agents'].append(agent)

	# Notes
	resource_dict['notes'] = []

	note_keys = []
	for key in resource.keys():
		if re.findall('note', key):
			if key not in note_keys:
				note_keys.append(key)

	for key in note_keys:
		note_dict = make_note_dict(key, resource)
		if note_dict != None:
			resource_dict['notes'].append(note_dict)

	# Id
	resource_dict['id_0'] = str(resource['coll_id_1'])
	resource_dict['id_1'] = str(resource['coll_id_2'])
	if len(str(resource['coll_id_3'])) < 5:
		id_2 = addZeros(resource['coll_id_3'])
		resource_dict['id_2'] = id_2
	else:
		resource_dict['id_2'] = str(resource['coll_id_3'])

	# Extent
	resource_dict['extents'] = []
	extent = {}
	extent['jsonmodel_type'] = 'extent'
	extent['portion'] = 'whole'
	if resource['cont_sum'] != "":
		extent['container_summary'] = resource['cont_sum']
	if resource['extent_num'] != "":
		extent['number'] = str(int(resource['extent_num']))
	if resource['extent_type'] != "":
		extent['extent_type'] = resource['extent_type']
	if len(extent) > 2:
		resource_dict['extents'].append(extent)


	return resource_dict


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVfile", nargs="?", default="DEFAULT", help="Name of CSV file or file path to CSV file")
	argparser.add_argmuent("reponum", nargs="?", default="DEFAULT", help="Number of repository where resources will go")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	# Passed file
	FILE = cliArguments.CSVfile

	# Reading file
	csv_file = pd.DataFrame(pd.read_csv(FILE, sep = ",", header = 0, index_col = False))
	
	# New JSON file name
	JSON_FILE = FILE[:-4] + ".json"
	
	# Transforming CSV file to JSON
	csv_file.to_json(JSON_FILE, orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

	# Loading JSON
	with open(JSON_FILE) as jsonfile:
		try:
			resources = json.load(jsonfile)
		except ValueError:
			logging.info('File not found.')
			exit(1)

	# Passing each resource array to the make_resource function
	REPO_NUM = cliArguments.reponum
	
	count = 0
	for resource in resources:
		count += 1
		print(count)
		try:
			resource = make_resource(resource)
			post_resource = aspace.post('/repositories/' + str(REPO_NUM) + '/resources', resource)
			pprint.pprint(post_resource)
		except:
			logging.info('Failed to make {}'.format(resource['title']))


