from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import csv
import unidecode
import re
import pandas as pd


def create_new_people_agent(name):
	''' Function to create new person agent '''

	agent = {'jsonmodel_type': 'agent_person',
			'names': [],
			'agent_type': 'agent_person'}

	name_dict = {}
	namex = name.split(',')
	if re.findall('--', name):
		name_dict['primary_name'] = name
	if len(re.findall(r'\d+', namex[-1])) != 0:
		name_dict['dates'] = namex[-1].strip()
	try:
		name_dict['primary_name'] = namex[0].strip()
	except:
		pass
	try:
		name_dict['rest_of_name'] = namex[1].strip()
	except:
		pass
	name_dict['is_display_name'] = True
	name_dict['jsonmodel_type'] = 'name_person'
	name_dict['name_order'] = 'inverted'
	name_dict['sort_name_auto_generate'] = True
	name_dict['rules'] = 'rda'

	agent['names'].append(name_dict)

	return agent


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)


	# csv = pd.read_csv('crosschecked_resources.csv')
	
	''' Code to create MRBC JSON file '''
	# csv_file = pd.DataFrame(pd.read_csv('crosschecked_resources.csv', sep = ",", header = 0, index_col = False))
	# csv_file.to_json("mrbc_to_aspace.json", orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

	with open("mrbc_to_aspace.json") as json_file:
		try:
			resources = json.load(json_file)
		except ValueError:
			logging.info('File not found')
			exit(1)

	# Extracting the keys that contain person agent data to be created
	person_keys = []
	for resource in resources:
		for key in resource.keys():
			if re.findall('person', key):
				if key not in person_keys:
					person_keys.append(key)

	# Pulling out the name values from the keys
	count = 0
	new_agent_names = {}
	new_agent_names['data'] = []
	errors = {}
	errors['data'] = []
	for resource in resources:
		for key in person_keys:
			if resource[key] != None and not 'agents' in resource[key]:
				name = unidecode.unidecode(resource[key])
				new_agent = create_new_people_agent(name)
				try:
					count += 1
					print(count)
					new_agent_created = aspace.post('agents/people', new_agent)
					pprint.pprint(new_agent_created)
					new_agent_names['data'].append((name, new_agent_created['uri']))
				except:
					logging.info('Agent failed to be created')
					errors['data'].append(new_agent)


	with open('new_agent_names.txt', 'w') as outfile:
		json.dump(new_agent_names, outfile)

	with open('agents_not_created.txt', 'w') as outfile:
		json.dump(errors, outfile)











