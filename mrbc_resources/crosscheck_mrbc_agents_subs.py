from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import csv
import unidecode
import re
import pandas as pd
import os
import string



if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	# Opening files for all agents and all subjects and MRBC resource metadata
	with open('all_subs_and_agents.json') as jfile:
		try:
			all_a_and_s = json.load(jfile)
		except ValueError:
			logging.info('File not found.')
			exit(1)

	## Code to transform MRBC csv into JSON 
	# csv_file = pd.DataFrame(pd.read_csv("mrbc_to_aspace.csv", sep = ",", header = 0, index_col = False))
	# csv_file.to_json("mrbc_to_aspace.json", orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

	# MRBC JSON
	with open('mrbc_to_aspace.json') as json_file:
		try:
			mrbc_resources = json.load(json_file)
		except ValueError:
			logging.info('File not found.')
			exit(1)


	# Pulling out only necessary keys 
	as_keys = []
	for resource in mrbc_resources:
		for key in resource.keys():
			if re.findall('creator', key) or re.findall('sub', key):
				if key not in as_keys:
					as_keys.append(key)


	# Getting the values for the Agent and Subject keys from the MRBC Resources JSON
	agents_and_subs = []
	for resource in mrbc_resources:
		for key in as_keys:
			if resource[key] != None:
				agents_and_subs.append(resource[key])


	# Stripping out bad chars
	clean_agents_and_subs = []
	for i in agents_and_subs:
		clean_name = unidecode.unidecode(i)
		clean_agents_and_subs.append(clean_name)


	# Trying to figure out how to match names and uris and return back to mrbc spreadsheet
	count = 0
	name_uri_tups = []
	for name in all_a_and_s['RECORDS']:
		for i in clean_agents_and_subs:
			if name['title'] == i:
				name_uri_tup = (name['title'], name['uri']) # Only 34 matching subs and agents
				name_uri_tups.append(name_uri_tup)


	# Swapping in the uris for matching sub/agent names			
	for resource in mrbc_resources:
		for key in as_keys:
			for pair in name_uri_tups:
				if resource[key] != None:
					if pair[0] == unidecode.unidecode(resource[key]):
						resource[key] = pair[1]



	# Writing to a new CSV					
	keys = mrbc_resources[0].keys()
	with open('crosschecked_resources.csv', 'w') as output_file:
	    dict_writer = csv.DictWriter(output_file, keys)
	    dict_writer.writeheader()
	    dict_writer.writerows(mrbc_resources)


