from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import re
import pandas as pd



def make_note_dict(key, mrbc_resource):
	''' Function to get note dicts '''
	
	typ = ""
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

	if mrbc_resource[key] != "":
		if key == 'lang_mat_note':
			note = {}
			note['jsonmodel_type'] = 'note_singlepart'
			note['type'] = 'langmaterial'
			note['publish'] = True
			note['content'] = []
			note['content'].append(mrbc_resource[key])
		else:
			note = {}
			note['jsonmodel_type'] = 'note_multipart'
			note['publish'] = True
			note['type'] = typ
			note['subnotes'] = []
			content = {}
			content['content'] = mrbc_resource[key]
			content['jsonmodel_type'] = 'note_text'
			content['publish'] = True
			note['subnotes'].append(content)

		return note


def make_resource(mrbc_resource):
	''' Function to generate MRBC resource record '''
	
	resource = {}
	
	# Dates section
	resource['dates'] = []
	date_dict = {}
	date_dict['jsonmodel_type'] = 'date'
	date_dict['label'] = 'creation'
	if mrbc_resource['date_begin'] != "":
		date_dict['begin'] = str(int(mrbc_resource['date_begin']))
		date_dict['calendar'] = 'gregorian'
	if mrbc_resource['date_end'] != "":
		date_dict['end'] = str(int(mrbc_resource['date_end']))
	if mrbc_resource['date_exp'] != "":
		date_dict['expression'] = str(mrbc_resource['date_exp'])
	if mrbc_resource['date_type'] != "":
		date_dict['date_type'] = str(mrbc_resource['date_type'].lower())
	if mrbc_resource['date_certainty'] != "":
		date_dict['certainty'] = mrbc_resource['date_certainty'].lower()
	if len(date_dict.keys()) > 2:
		resource['dates'].append(date_dict)

	# Language
	resource['language'] = 'eng'

	# Level
	resource['level'] = 'collection'

	# Title
	resource['title'] = mrbc_resource['title']

	# Subjects
	resource['subjects'] = []

	sub_keys = []
	for key in mrbc_resource.keys():
		if re.findall('geo', key) or re.findall('genform', key) or re.findall('top', key) or re.findall('un_title', key):
			if key not in sub_keys:
				sub_keys.append(key)

	for key in sub_keys:
		if mrbc_resource[key] != "":
			sub = {'ref': mrbc_resource[key]}
			resource['subjects'].append(sub)

	# Agents
	resource['linked_agents'] = []

	ag_keys = []
	for key in mrbc_resource.keys():
		if re.findall('person', key) or re.findall('family', key) or re.findall('corp_body', key):
			if key not in ag_keys:
				ag_keys.append(key)

	for key in ag_keys:
		if re.findall('creator', key):
			if mrbc_resource[key] != "":
				agent = {}
				agent['ref'] = mrbc_resource[key]
				agent['role'] = 'creator'
				agent['terms'] = []
				resource['linked_agents'].append(agent)
		else:
			if mrbc_resource[key] != "":
				agent = {}
				agent['ref'] = mrbc_resource[key]
				agent['role'] = 'subject'
				agent['terms'] = []
				resource['linked_agents'].append(agent)

	# Notes
	resource['notes'] = []

	note_keys = []
	for key in mrbc_resource.keys():
		if re.findall('note', key):
			if key not in note_keys:
				note_keys.append(key)

	for key in note_keys:
		note_dict = make_note_dict(key, mrbc_resource)
		if note_dict != None:
			resource['notes'].append(note_dict)

	# Id
	resource['id_0'] = str(mrbc_resource['coll_id_1'])
	resource['id_1'] = str(mrbc_resource['coll_id_2'])
	resource['id_2'] = str(mrbc_resource['coll_id_3'])

	# Extent
	resource['extents'] = []
	extent = {}
	extent['jsonmodel_type'] = 'extent'
	extent['portion'] = 'whole'
	if mrbc_resource['cont_sum'] != "":
		extent['container_summary'] = mrbc_resource['cont_sum']
	if mrbc_resource['extent_num'] != "":
		extent['number'] = str(int(mrbc_resource['extent_num']))
	if mrbc_resource['extent_type'] != "":
		extent['extent_type'] = mrbc_resource['extent_type']
	if len(extent) > 2:
		resource['extents'].append(extent)


	return resource


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)


	# csv_file = pd.DataFrame(pd.read_csv('final_pass.csv', sep = ",", header = 0, index_col = False))
	# csv_file.to_json("mrbc_to_aspace.json", orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

	# os.system("open mrbc_to_aspace.json")

	with open('mrbc_to_aspace.json') as jsonfile:
		try:
			resources = json.load(jsonfile)
		except ValueError:
			logging.info('File not found.')
			exit(1)

	
	count = 0
	for resource in resources:
		count += 1
		print(count)
		try:
			resource = make_resource(resource)
			post_resource = aspace.post('/repositories/3/resources', resource)
			pprint.pprint(post_resource)
		except:
			pprint.pprint(resource['title'])


