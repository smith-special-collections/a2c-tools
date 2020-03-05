from archivesspace import archivesspace
import argparse
import logging
import datetime
import csv


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
		acc_dict['id_0'] = str(int(accession['id_0'])).strip()
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
		if '.' in str(accession['id_3']):
			i3 = str(accession['id_3']).split('.')
			acc_dict['id_3'] = i3[1]
			if len(acc_dict['id_3']) < 4:
				while len(acc_dict['id_3']) < 4:
					acc_dict['id_3'] = acc_dict['id_3'] + '0'
		else:
			acc_dict['id_3'] = str(accession['id_3']).strip()
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
		extent_dict['extent_type'] = accession['extent_type'].lower().strip() + 's'
	except:
		pass
	try:
		extent_dict['number'] = str(int(accession['extent'])).strip()
	except:
		pass
	try:
		extent_dict['portion'] = accession['portion'].lower().strip()
	except:
		pass

	# Ensures extents array has all the required fields, otherwise an error will be raised when trying to post	
	if len(extent_dict) > 3:
		acc_dict['extents'].append(extent_dict)			 

	# Date field
	acc_dict['dates'] = []
	date_dict = {}

	if accession['date_type'] != None and accession['begin_date'] != None:
		if accession['date_type'].lower().strip() == 'inclusive':
			date_dict['end'] = accession['end_date']
		if len(str(accession['begin_date'])) > 4 or len(str(accession['begin_date'])) < 4:
			date_dict['begin'] = '0000'
		else:
			date_dict['begin'] = str(int(accession['begin_date']))
		if accession['certainty'] != None and (accession['certainty'].lower().strip() == 'approximate' or accession['certainty'].lower().strip() == 'inferred' or accession['certainty'].lower().strip() == 'questionable'):
			date_dict['certainty'] = accession['certainty'].strip()
		date_dict['date_type'] = accession['date_type'].lower().strip()
		date_dict['calendar'] = 'gregorian'
		date_dict['era'] = 'ce'
		date_dict['jsonmodel_type'] = 'date'
		date_dict['label'] = 'publication'
		acc_dict['dates'].append(date_dict)

	# Acquisition Type
	try:
		acc_dict['acquisition_type'] = accession['\ufeffacquisition_type'].lower().strip()
	except:
		pass
	
	# Linked agents
	acc_dict['linked_agents'] = []

	if accession['agent_type1'] != None:
		for key in RELATOR_DICT.keys():
			if key == accession['agent_type1'].lower().strip():
				relator1 = RELATOR_DICT[key]
			else:
				relator1 = ""

	if accession['agent_type2'] != None:
		for key in RELATOR_DICT.keys():
			if key == accession['agent_type2'].lower().strip():
				relator2 = RELATOR_DICT[key]
			else:
				relator2 = ""

	agent1 = {}
	agent1['terms'] = []
	try:
		if accession['agent_uri1'][0] == '/':
			agent1['ref'] = accession['agent_uri1'].strip()
			if relator1 != "":
				agent1['relator'] = relator1
			if accession['linked_agent_role1'].strip() != None:
				agent1['role'] = accession['linked_agent_role1'].lower().strip()

			acc_dict['linked_agents'].append(agent1)
	except:
		pass

	agent2 = {}
	agent2['terms'] = []
	try:
		if accession['agent_uri2'][0] == '/':
			agent2['ref'] = accession['agent_uri2'].strip()
			if relator2 != "":
				agent2['relator'] = relator1
			if accession['linked_agent_role2'].strip() != None:	
				agent2['role'] = accession['linked_agent_role2'].lower().strip()

			acc_dict['linked_agents'].append(agent2)
	except:
		pass

	# Payments module
	payment_summary = {}
	payment_summary['payments'] = []
	payment_info = {}
	if accession['total_price'] != None:
		payment_summary['total_price'] = str(accession['total_price']).strip()
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
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVname", default="DEFAULT", help="Name of the CSV spreadsheet, e.g, 'duplaix.csv. Note: It must be in the same directory as this code file.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	csv_file = cliArguments.CSVname

	# Reads CSV file
	with open(csv_file, encoding="utf8", errors="ignore") as csvfile:
		reader = csv.DictReader(csvfile)

		for row in reader:
			if row['complete'] == 'TRUE':
				record = make_accession_record(row)
				try:
					post = aspace.post('/repositories/3/accessions', record)
					logging.info('Accession record created for {}'.format(row['title']))
				except Exception as e:
					logging.warning('Failure to create accession record for {}: {}'.format(row['title'], e))
	


