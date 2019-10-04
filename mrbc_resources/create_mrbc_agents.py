from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
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
	if re.match('--', name):
		name_dict['primary_name'] = name
	if len(re.match(r'\d+', namex[-1])) != 0:
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


def create_new_corp_agent(name):
	''' Function to create new corporate agent '''

	agent = {'jsonmodel_type': 'agent_corporate_entity',
	'names': [],
	'agent_type': 'agent_corporate_entity'}

	name_dict = {}
	name_dict['primary_name'] = name
	name_dict['rules'] = 'rda'
	name_dict['jsonmodel_type'] = 'name_corporate_entity'
	name_dict['sort_name_auto_generate'] = True
	name_dict['is_display_name'] = True

	agent['names'].append(name_dict)

	return agent


def create_new_topical_sub(name):
	''' Function to create new topical subject '''

	subject = { "jsonmodel_type":"subject",
	"external_ids":[],
	"publish": True,
	"is_slug_auto": True,
	"used_within_repositories":[],
	"used_within_published_repositories":[],
	"terms":[{ "jsonmodel_type":"term",
	"term": name,
	'vocabulary': '/vocabularies/1',
	"term_type":"topical"}],
	"external_documents":[],
	"source":"local",
	'vocabulary': '/vocabularies/1'}

	return subject


def create_new_geographical_sub(name):
	''' Function to create new topical subject '''

	subject = { "jsonmodel_type":"subject",
	"external_ids":[],
	"publish": True,
	"is_slug_auto": True,
	"used_within_repositories":[],
	"used_within_published_repositories":[],
	"terms":[{ "jsonmodel_type":"term",
	"term": name,
	'vocabulary': '/vocabularies/1',
	"term_type":"geographical"}],
	"external_documents":[],
	"source":"local",
	'vocabulary': '/vocabularies/1'}

	return subject


def create_new_genre_sub(name):
	''' Function to create new topical subject '''

	subject = { "jsonmodel_type":"subject",
	"external_ids":[],
	"publish": True,
	"is_slug_auto": True,
	"used_within_repositories":[],
	"used_within_published_repositories":[],
	"terms":[{ "jsonmodel_type":"term",
	"term": name,
	'vocabulary': '/vocabularies/1',
	"term_type":"genre_form"}],
	"external_documents":[],
	"source":"local",
	'vocabulary': '/vocabularies/1'}

	return subject


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVFILE", default="DEFAULT", help="Name of the CSV file with agents data.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	csv = cliArguments.CSVFILE

	
	# Code to create MRBC JSON object 
	csv_file = pd.DataFrame(pd.read_csv(csv, sep = ",", header = 0, index_col = False))
	resources = csv_file.to_dict('records')

	# Extracting the keys that contain person agent data to be created
	keys = []
	for resource in resources:
		for key in resource.keys():
			if re.match('genform', key):
				if key not in keys:
					keys.append(key)


	for resource in resources:
		for key in keys:
			if resource[key] != None:
				print(resource[key])


	# Pulling out the name values from the keys
	count = 0
	new_agent_names = {}
	new_agent_names['data'] = []
	errors = {}
	errors['data'] = []
	for resource in resources:
		for key in keys:
			if resource[key] != None and not 'subjects' in resource[key]:
				name = unidecode.unidecode(resource[key])
				new_agent = create_new_genre_sub(name)
				pprint.pprint(new_agent)
				try:
					count += 1
					print(count)
					new_agent_created = aspace.post('/subjects', new_agent)
					pprint.pprint(new_agent_created)
					new_agent_names['data'].append((name, new_agent_created['uri']))
				except:
					logging.info('Subject failed to be created')
					errors['data'].append(new_agent)


	with open('new_agent_names.txt', 'w') as outfile:
		json.dump(new_agent_names, outfile)

	with open('agents_not_created.txt', 'w') as outfile:
		json.dump(errors, outfile)







