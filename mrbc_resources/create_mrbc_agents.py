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
	name = name.split(',')
	if len(re.findall(r'\d+', name[-1])) != 0:
		name_dict['dates'] = name[-1].strip()
	try:
		name_dict['primary_name'] = name[0].strip()
	except:
		pass
	try:
		name_dict['rest_of_name'] = name[1].strip()
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


	csv = pd.read_csv('mrbc_agents.csv')
	agents = csv.creator_person # Column name

	names = []
	for agent in agents:
		name = unidecode.unidecode(agent)
		names.append(name)

	count = 0
	new_uris = []
	for name in names:
		if len(name) != 0:
			count += 1
			new_agent = create_new_people_agent(name)
			try:
				new_agent_created = aspace.post('agents/people', new_agent)
				print(count)
				new_uris.append(new_agent_created['uri'])
			except:
				pprint.pprint(new_agent)


	csv_input = pd.read_csv('mrbc_agents.csv')
	csv_input['agent_uri'] = new_uris
	print(csv_input)
	csv_input.to_csv('pandas_test.csv', index=False)

	# test = aspace.get('/agents/people/45863')
	# pprint.pprint(test)




