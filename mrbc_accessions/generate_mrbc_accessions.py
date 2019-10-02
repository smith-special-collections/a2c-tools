from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import pandas as pd
import datetime


RELATOR_DICT = {
	'artist': 'art',
	'author': 'aut',
	'donor': 'dnr',
	'editor': 'edt',
	'publisher': 'pbl',
	'translator': 'trl'
}

DATE = datetime.date.today()
DATE = DATE.__str__()

def make_accession_record(accession):
	'''Function to make MRBC accessions connected to parent lots'''

	acc_dict = {'access_restrictions': False,
				 'accession_date': DATE,
				 'classifications': [],
				 'deaccessions': [],
				 'external_documents': [],
				 'external_ids': [],
				 'instances': [],
				 'jsonmodel_type': 'accession',
				 'linked_events': [],
				 'publish': False,
				 'related_resources': [],
				 'repository': {'ref': '/repositories/3'},
				 'restrictions_apply': False,
				 'rights_statements': [],
				 'subjects': [],
				 'suppressed': False,
				 'title': accession['title'],
				 'use_restrictions': False}

	# Related accessions
	acc_dict['related_accessions'] = []
	rel_acc = {}
	rel_acc['jsonmodel_type'] = 'accession_parts_relationship'
	rel_acc['relator'] = 'forms_part_of'
	rel_acc['relator_type'] = 'part'
	try:
		rel_acc['ref'] = accession['related_accessions']
		acc_dict['related_accessions'].append(rel_acc)
	except:
		pass
				 
	# Provenance
	if accession['provenance'] != None:
		acc_dict['provenance'] = accession['provenance']
	else:
		pass

	# Resource type
	try:
		acc_dict['resource_type'] = accession['resource_type'].lower()
	except:
		pass

	# Id
	try:
		acc_dict['id_0'] = str(int(accession['id_0']))
	except:
		pass
	try:
		acc_dict['id_1'] = accession['id_1']
	except:
		pass
	try:
		i2 = str(accession['id_2']).split('.')
		acc_dict['id_2'] = i2[1]
		if len(acc_dict['id_2']) < 4:
			while len(acc_dict['id_2']) < 4:
				acc_dict['id_2'] = acc_dict['id_2'] + '0'
	except:
		pass
	try:
		i3 = str(accession['id_3']).split('.')
		acc_dict['id_3'] = i3[1]
		if len(acc_dict['id_3']) < 4:
			while len(acc_dict['id_3']) < 4:
				acc_dict['id_3'] = acc_dict['id_3'] + '0'
	except:
		pass

	# Content Description
	if accession['content_description'] != None:
		acc_dict['content_description'] = accession['content_description']

	# Extents
	acc_dict['extents'] = []
	extent_dict = {}
	extent_dict['jsonmodel_type'] = 'extent'
	try:
		extent_dict['extent_type'] = accession['extent_type'].lower() + 's'
	except:
		pass
	try:
		extent_dict['number'] = str(int(accession['extent']))
	except:
		pass
	try:
		extent_dict['portion'] = accession['portion'].lower()
	except:
		pass

	# Ensures extents array has all the required fields, otherwise an error will be raised when trying to post	
	if len(extent_dict) > 3:
		acc_dict['extents'].append(extent_dict)			 

	# Date field
	acc_dict['dates'] = []
	date_dict = {}

	if accession['date_type'] != None and accession['begin_date'] != None:
		if accession['date_type'].lower() == 'inclusive':
			date_dict['end'] = accession['end_date']
		if len(str(accession['begin_date'])) > 4 or len(str(accession['begin_date'])) < 4:
			date_dict['begin'] = '0000'
		else:
			date_dict['begin'] = str(int(accession['begin_date']))
		if accession['certainty'] != None and (accession['certainty'].lower() == 'approximate' or accession['certainty'].lower() == 'inferred' or accession['certainty'].lower() == 'questionable'):
			date_dict['certainty'] = accession['certainty']
		date_dict['date_type'] = accession['date_type'].lower()
		date_dict['calendar'] = 'gregorian'
		date_dict['era'] = 'ce'
		date_dict['jsonmodel_type'] = 'date'
		date_dict['label'] = 'publication'
		acc_dict['dates'].append(date_dict)

	# Acquisition Type
	try:
		acc_dict['acquisition_type'] = accession['acquisition_type'].lower()
	except:
		pass
	
	# Linked agents
	acc_dict['linked_agents'] = []

	if accession['agent_type1'] != None:
		for key in RELATOR_DICT.keys():
			if key == accession['agent_type1'].lower():
				relator1 = RELATOR_DICT[key]
			else:
				relator1 = ""

	if accession['agent_type2'] != None:
		for key in RELATOR_DICT.keys():
			if key == accession['agent_type2'].lower():
				relator2 = RELATOR_DICT[key]
			else:
				relator2 = ""


	agent1 = {}
	agent1['terms'] = []
	if accession['agent_uri1'] != None:
		agent1['ref'] = accession['agent_uri1']
		if relator1 != "":
			agent1['relator'] = relator1
		if accession['linked_agent_role1'] != None:
			agent1['role'] = accession['linked_agent_role1'].lower()

		acc_dict['linked_agents'].append(agent1)

	agent2 = {}
	agent2['terms'] = []
	if accession['agent_uri2'] != None:
		agent2['ref'] = accession['agent_uri2']
		if relator2 != "":
			agent2['relator'] = relator1
		if accession['linked_agent_role2'] != None:
			agent2['role'] = accession['linked_agent_role2'].lower()

		acc_dict['linked_agents'].append(agent2)

	# Payments module
	payment_summary = {}
	payment_summary['payments'] = []
	payment_info = {}
	if accession['total_price'] != None:
		payment_summary['total_price'] = str(accession['total_price'])
		payment_summary['currency'] = 'USD'
		payment_summary['in_lot'] = False
		payment_summary['jsonmodel_type'] = 'payment_summary'
	if accession['payment_date'] != None:
		payment_info['payment_date'] = accession['payment_date']
	if accession['authorizer'] == 'Shannon Supple' or accession['authorizer'] == 'Shannon':
		payment_info['jsonmodel_type'] = 'payment'
		payment_info['authorizer'] = {}
		payment_info['authorizer']['ref'] = '/agents/people/16'
	if len(payment_info) != 0:
		payment_summary['payments'].append(payment_info)
		acc_dict['payment_summary'] = payment_summary

	return acc_dict


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVname", nargs="?", default="DEFAULT", help="Name of the CSV spreadsheet, e.g, 'duplaix.csv. Note: It must be in the same directory as this code file.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	FILE = cliArguments.CSVname


	# Reads CSV file
	csv_file = pd.DataFrame(pd.read_csv(FILE, sep = ",", header = 0, index_col = False))
	
	# Transforms CSV file into a list of Python dictionary objects
	accessions = csv_file.to_dict('records')
	
	# Iterates over individual accessions
	errors = {}
	errors['rows'] = []

	count = 0
	for accession in accessions:
		if accession['complete'] == True:
			count += 1
			logging.info(count)
			record = make_accession_record(accession)
			pprint.pprint(record)	
			try:
				post = aspace.post('/repositories/3/accessions', record)
				logging.info('Accession record created for {}'.format(accession['title']))
			except Exception as e:
				error_string = 'Unable to post accession because of metadata errors. Check data for {}'.format(accession['title'])
				logging.info(error_string)
				errors['rows'].append(e)

	pprint.pprint(errors['rows'])

