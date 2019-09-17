import json
from archivesspace import archivesspace
import pprint
import argparse
import logging
import random
from collections import Counter
import time
import csv


def getDupeSetAspaceRecords(dupe_cluster):
	'''Function to get a set of Aspace records'''
	record_set = []
	for dupe in dupe_cluster['dupes']:
		record = aspace.get(dupe['uri'])
		record_set.append(record)

	return record_set

## For mult_dupes only
def determineSurvivorForMultFalses(dupe_aspace_record_set):
	'''Function to determine a Survivor for dupe sets with only multiple Falses'''

	record_set = dupe_aspace_record_set
	record_set[0]['live'] = True

	return record_set

## For mult_dupes only
def determineSoleSurvivor(dupe_aspace_record_set):
	'''Function to identify a single Survivor for dupe sets with multiple Trues'''

	true_records = []
	new_record_set = []
	record_set = dupe_aspace_record_set

	for record in record_set:
		if record['live'] == True:
			true_records.append(record)
		elif record['live'] == False:
			new_record_set.append(record)
		else:
			pass

	# Set all True records to False temporarily		
	for record in true_records:
		record['live'] = False

	# Determine 1st record as Survivor
	true_records[0]['live'] = True

	for record in true_records:
		new_record_set.append(record)

	if len(record_set) == len(new_record_set):
		# logging.error('Sole survivor determined!')
		return new_record_set
	else:
		# logging.error('Revisit!')
		return None


## For two_dupes only
def determineSurvivorForPairWithTwoFalsesOrTwoTrues(dupe_aspace_record_set):
	'''Function to determine a Survivor for any record pair with two falses or two trues'''

	true_count = 0
	for dupe in dupe_aspace_record_set:
		if dupe['live'] == True:
			true_count += 1

	# If double true
	if true_count > 1:
		dupe_aspace_record_set[0]['live'] = False

	# If double false
	if true_count < 1:
		dupe_aspace_record_set[0]['live'] = True

	return dupe_aspace_record_set


def getSurvivor(dupe_aspace_record_set):
	'''Function to determine Survivor of Record Set'''	
		
	for record in dupe_aspace_record_set:
		record['live'] = ""
		try:
			if 'rest_of_name' in record['names'][0].keys():
				record['live'] = True
			else:
				record['live'] = False
		except:
			pass

	return dupe_aspace_record_set


def countLives(dupe_aspace_record_set):
	'''Debugging tool to verify number of records and survivor values from ArchivesSpace record sets
	Returns number of records and their survivor status'''
	
	report = {}
	mythings = set()
	# Get list of keys for my report
	for record in record_set:
		mythings.add("%s" % record['live'])
	# Initialize values in report to 0
	for thing in mythings:
		report[thing] = 0
	for record in record_set:
		report["%s" % record['live']] += 1

	total = 0
	for thingtotal in report.keys():
		total = total + report[thingtotal]
			
	report['total'] = total
			
	return report


def getVictimNotes(victim_aspace_record):
	'''Function to get notes from Victim to be given to Survivor

	>>> test = {'notes': [{'jsonmodel_type': 'note_bioghist',
	...	'label': 'Agent notes',
	...	'persistent_id': 'ce0dc6544857504ea2967f3691dd045d',
	...	'publish': False,
	...	'subnotes': [{'content': 'SSC video SR',
	...	'jsonmodel_type': 'note_text',
	...	'publish': False}]},
	...	{'jsonmodel_type': 'note_bioghist',
	...	'persistent_id': 'cce0922171eaeb0d5f6dfa1068d76cf2',
	...	'publish': True,
	...	'subnotes': [{'content': 'Class of 1944.',
	...	'jsonmodel_type': 'note_text',
	...	'publish': True}]}]}
	>>> new_notes = getVictimNotes(test)
	>>> new_notes
	[{'jsonmodel_type': 'note_bioghist', 'label': 'Agent notes', 'publish': False, 'subnotes': [{'content': 'SSC video SR', 'jsonmodel_type': 'note_text', 'publish': False}]}, {'jsonmodel_type': 'note_bioghist', 'publish': True, 'subnotes': [{'content': 'Class of 1944.', 'jsonmodel_type': 'note_text', 'publish': True}]}]
	>>> 
	'''

	if len(victim_aspace_record['notes']) != 0:
		notes = victim_aspace_record['notes']

		new_notes = []
		for note in notes:
			new_note = {}
			new_note['jsonmodel_type'] = note['jsonmodel_type']
			try:
				new_note['label'] = note['label']
			except:
				pass
			new_note['publish'] = note['publish']
			new_note['subnotes'] = note['subnotes']
			new_notes.append(new_note)

		return new_notes

	else:
		return None


def getVictimAgentContacts(victim_aspace_record):
	'''Function to get Agent Contacts from victim

	>>> agent_contacts = {'agent_contacts':[{'address_2': 'Linda Manor',
	...   'city': 'Northampton',
	...   'create_time': '2018-10-12T14:44:01Z',
	...   'created_by': 'mwhite',
	...   'jsonmodel_type': 'agent_contact',
	...   'last_modified_by': 'mwhite',
	...   'lock_version': 0,
	...   'name': 'Joann Aalfs',
	...   'note': "SSC video V; Also donor of New Bedford Women's Awareness Group "
	...           'Records (coll ID 480); test; Daughter Janet Aals main contact now '
	...           '(10/7/16)',
	...   'post_code': '1060',
	...   'region': 'MA',
	...   'system_mtime': '2018-11-12T19:51:10Z',
	...   'telephones': [{'create_time': '2018-10-12T14:44:01Z',
	...                   'created_by': 'mwhite',
	...                   'jsonmodel_type': 'telephone',
	...                   'last_modified_by': 'mwhite',
	...                   'number': '(413) 586-0862',
	...                   'number_type': 'business',
	...                   'system_mtime': '2018-10-12T14:44:01Z',
	...                   'uri': '/telephone/1826',
	...                   'user_mtime': '2018-10-12T14:44:01Z'}],
	...   'user_mtime': '2018-10-12T14:44:01Z'}]}
	>>> getVictimAgentContacts(agent_contacts)
	{'jsonmodel_type': 'agent_contact', 'name': 'Joann Aalfs', 'note': "SSC video V; Also donor of New Bedford Women's Awareness Group Records (coll ID 480); test; Daughter Janet Aals main contact now (10/7/16)", 'telephones': [{'jsonmodel_type': 'telephone', 'number': '(413) 586-0862', 'number_type': 'business', 'uri': '/telephone/1826'}]}
	>>> 		
	'''

	if len(victim_aspace_record['agent_contacts']) != 0:
		agent_contacts = victim_aspace_record['agent_contacts']

		new_agentcontacts = []
		for ac in agent_contacts:
			new_agentcontact = {}
			new_agentcontact['jsonmodel_type'] = ac['jsonmodel_type']
			try:
				new_agentcontact['address_1'] = ac['address_1']
			except:
				pass
			try:
				new_agentcontact['email'] = ac['email']
			except:
				pass
			try:
				new_agentcontact['name'] = ac['name']
			except:
				pass
			try:
				new_agentcontact['note'] = ac['note']
			except:
				pass
			if len(ac['telephones']) != 0:
				try:
					new_agentcontact['telephones'] = []

					for phone in ac['telephones']:
						telephone = {}
						try:
							telephone['jsonmodel_type'] = phone['jsonmodel_type']
						except:
							pass
						try:
							telephone['number'] = phone['number']
						except:
							pass
						try:
							telephone['number_type'] = phone['number_type']
						except:
							pass
						try:
							telephone['uri'] = phone['uri']
						except:
							pass

						new_agentcontact['telephones'].append(telephone)
				except:
					pass

			new_agentcontacts.append(new_agentcontact)
		return new_agentcontacts

	else:
		return None


def getVictimDates(victim_aspace_record):
	'''Function to get Dates of Existence from Victim

	>>> dates = {'dates_of_existence': [{'begin': '1957-08-16',
	... 'calendar': 'gregorian',
	... 'create_time': '2018-10-18T18:04:34Z',
	... 'created_by': 'mwhite',
	... 'date_type': 'single',
	... 'era': 'ce',
	... 'expression': '1957 August 16',
	... 'jsonmodel_type': 'date',
	... 'label': 'existence',
	... 'last_modified_by': 'mwhite',
	... 'lock_version': 0,
	... 'system_mtime': '2018-10-18T18:04:34Z',
	... 'user_mtime': '2018-10-18T18:04:34Z'}]}
	>>> getVictimDates(dates)
	[{'jsonmodel_type': 'date', 'date_type': 'single', 'begin': '1957-08-16', 'label': 'existence', 'calendar': 'gregorian', 'era': 'ce', 'expression': '1957 August 16'}]
	>>>
	'''

	if len(victim_aspace_record['dates_of_existence']) != 0:
		does = victim_aspace_record['dates_of_existence']

		new_does = []
		for doe in does:
			new_doe = {}
			new_doe['jsonmodel_type'] = doe['jsonmodel_type']
			new_doe['date_type'] = doe['date_type']
			try:
				new_doe['begin'] = doe['begin']
			except:
				pass
			try:
				new_doe['end'] = doe['end']
			except:
				pass
			try:
				new_doe['label'] = doe['label']
			except:
				pass
			try:
				new_doe['calendar'] = doe['calendar']
			except:
				pass
			try:
				new_doe['era'] = doe['era']
			except:
				pass
			try:
				new_doe['expression'] = doe['expression']
			except:
				pass
			new_does.append(new_doe)

		return new_does

	else:
		return None


def getVictimExternalDocuments(victim_aspace_record):
	'''Function to get External Documents from victim

	>>> record = {'external_documents': [{'create_time': '2017-11-13T14:59:55Z',
	... 'created_by': 'vteeter',
	... 'jsonmodel_type': 'external_document',
	... 'last_modified_by': 'vteeter',
	... 'location': 'http://www.ppseawa.org/',
	... 'lock_version': 0,
	... 'publish': False,
	... 'system_mtime': '2017-11-13T14:59:55Z',
	... 'title': 'Website',
	... 'user_mtime': '2017-11-13T14:59:55Z'}]}
	>>> getVictimExternalDocuments(record)
	[{'jsonmodel_type': 'external_document', 'location': 'http://www.ppseawa.org/', 'publish': False, 'title': 'Website'}]
	>>> 	
	'''

	if len(victim_aspace_record['external_documents']) != 0:
		ext_docs = victim_aspace_record['external_documents']
		
		new_docs = []
		for doc in ext_docs:
			new_doc = {}
			new_doc['jsonmodel_type'] = doc['jsonmodel_type']
			try:
				new_doc['location'] = doc['location']
			except:
				pass
			new_doc['publish'] = doc['publish']
			try:
				new_doc['title'] = doc['title']
			except:
				pass
			new_docs.append(new_doc)

		return new_docs 

	else:
		return None


def getVictimRelatedAgents(victim_aspace_record):
	'''Function to get Related Agents from Victim

	>>> related_agents = {'related_agents': [{'create_time': '2017-11-02 17:51:50 UTC',
	... 'created_by': 'knutter',
	... 'jsonmodel_type': 'agent_relationship_associative',
	... 'last_modified_by': 'knutter',
	... 'ref': '/agents/people/40908',
	... 'relator': 'is_associative_with',
	... 'system_mtime': '2017-11-02 17:51:50 UTC',
	... 'user_mtime': '2017-11-02 17:51:50 UTC'}]}
	>>> getVictimRelatedAgents(related_agents)
	[{'jsonmodel_type': 'agent_relationship_associative', 'ref': '/agents/people/40908', 'relator': 'is_associative_with'}]
	>>> 
	'''

	if len(victim_aspace_record['related_agents']) != 0:
		related_agents = victim_aspace_record['related_agents']

		new_relatedagents = []
		for agent in related_agents:
			new_relatedagent = {}
			new_relatedagent['jsonmodel_type'] = agent['jsonmodel_type']
			new_relatedagent['ref'] = agent['ref']
			new_relatedagent['relator'] = agent['relator']
			new_relatedagents.append(new_relatedagent)

		return new_relatedagents

	else:
		return None


def getVictimNameData(victim_aspace_record):
	'''Function to get Name data (like Source, etc.) from Victim 
	
	>>> names = {'names': [{'authorized': True,
	... 'create_time': '2017-07-26T17:48:52Z',
	... 'created_by': 'dmayo',
	... 'is_display_name': True,
	... 'jsonmodel_type': 'name_person',
	... 'last_modified_by': 'dmayo',
	... 'lock_version': 0,
	... 'name_order': 'inverted',
	... 'primary_name': 'Abbott, Jere, 1897-1982',
	... 'sort_name': 'Abbott, Jere, 1897-1982',
	... 'sort_name_auto_generate': True,
	... 'source': 'naf',
	... 'system_mtime': '2018-11-27T23:11:36Z',
	... 'user_mtime': '2017-07-26T17:48:52Z'}]}
	>>> getVictimNameData(names)
	[{'jsonmodel_type': 'name_person', 'is_display_name': False, 'source': 'naf', 'primary_name': 'Abbott, Jere, 1897-1982'}]
	>>>
	'''
	
	names = victim_aspace_record['names']

	try:
		new_names = []
		for name in names:
			if name['jsonmodel_type'] != 'name_family':
				new_name = {}
				new_name['jsonmodel_type'] = name['jsonmodel_type']
				new_name['is_display_name'] = False
				try:
					new_name['source'] = name['source']
				except:
					pass
				try:
					new_name['primary_name'] = name['primary_name']
				except:
					pass
				try:
					new_name['rest_of_name'] = name['rest_of_name']
				except:
					pass
				try:
					new_name['name_order'] = name['name_order']
				except:
					pass
				try:
					new_name['rules'] = name['rules']
				except:
					pass
				try:
					new_name['authority_id'] = name['authority_id']
				except:
					pass
				new_name['sort_name_auto_generate'] = True
				new_names.append(new_name)
			else:
				new_name = {}
				new_name['jsonmodel_type'] = name['jsonmodel_type']
				new_name['is_display_name'] = False
				try:
					new_name['source'] = name['source']
				except:
					pass
				try:
					new_name['family_name'] = name['family_name']
				except:
					pass
				try:
					new_name['use_dates'] = name['use_dates']
				except:
					pass
				try:
					new_name['authority_id'] = name['authority_id']
				except:
					pass
				new_name['sort_name_auto_generate'] = True
				new_names.append(new_name)

		return new_names

	except:
		return None


#######################################################
''' This set of functions gives and updates linked records for surviving Agent records '''

def getLinkedAgentRoles(aspace_record_set):
	'''Function to get Linked Record roles for Agents'''

	try:
		for record in aspace_record_set:
			record['linked_agent_roles'] = []
			for linked_record in record['linked_records']:
				lr = aspace.get(linked_record)
				for agent in lr['linked_agents']:
					if agent['ref'] == record['uri']:
						uri = lr['uri']
						role = agent['role']
						if 'relator' in agent.keys():
							relator = agent['relator']
						else:
							relator = 'no_relator'
						record['linked_agent_roles'].append((uri, role, relator)) # 6/11/19 -- attempting to add relator 
	except:
		for record in aspace_record_set:
			logging.info('Could not get linked agent role for Agent {}'.format(record['title']))

	return aspace_record_set


def giveSurvivorLinkedRecords(aspace_record_set_with_survivor_determined):
	'''Function to give Survivor linked records

	>>> record_set = [{'linked_agent_roles': [('/repositories/2/resources/775', 'creator')],
	...   'linked_records': [('/repositories/2/resources/775', 'creator'),
	...                      ('/repositories/2/resources/775', 'subject')],
	...   'live': True},
	...  {'linked_agent_roles': [('/repositories/2/resources/775', 'subject')],
	...   'linked_records': ['/repositories/2/resources/775'],
	...   'live': False}]
	>>> giveSurvivorLinkedRecords(record_set)
	[{'linked_agent_roles': [('/repositories/2/resources/775', 'creator')], 'linked_records': [('/repositories/2/resources/775', 'creator'), ('/repositories/2/resources/775', 'subject')], 'live': True}, {'linked_agent_roles': [('/repositories/2/resources/775', 'subject')], 'linked_records': ['/repositories/2/resources/775'], 'live': False}]
	>>> 
	'''

	aspace_record_set = aspace_record_set_with_survivor_determined
	all_linked_records = []
	for record in aspace_record_set:
		for lr in record['linked_agent_roles']:
			if lr not in all_linked_records: 
				all_linked_records.append(lr)

	try:
		for record in aspace_record_set:
			if record['live'] == True:
				record['linked_records'] = all_linked_records
	except:
		logging.info('Failed to give Survivor linked records')
		pass

	return aspace_record_set

# For mult dupes
def updateSurvivorsLinkedRecords(survivor_uri, linked_record_of_survivor_aspace_record):
	''' Function to individually attempt to link records to the Survivor '''
	lr = linked_record_of_survivor_aspace_record
	
	try:
		if lr[2] == 'no_relator':
			linked_agent = {'ref': survivor_uri, 'role': lr[1], 'terms': []}
			record = aspace.get(lr[0])
			record['linked_agents'].append(linked_agent)
			post_record = aspace.post(lr[0], record)
			return post_record
		else:
			linked_agent = {'ref': survivor_uri, 'role': lr[1], 'terms': [], 'relator': lr[2]}
			record = aspace.get(lr[0])
			record['linked_agents'].append(linked_agent)
			post_record = aspace.post(lr[0], record)
			return post_record
	except:
		logging.info('Updating failed for Linked Record {}'.format(lr[0]))
		string = 'FAIL! {} needs to be linked to {}'.format(survivor_uri, lr)
		return string


def updateSurvivorLinkedRecords(survivor_aspace_record):
	''' Function to update records linked to the Survivor '''
	
	posts = []

	try:
		for linked_record in survivor_aspace_record['linked_records']: # Add relator bit here
			if linked_record[2] == 'no_relator':
				linked_agent = {'ref': survivor_aspace_record['uri'], 'role': linked_record[1], 'terms': []}
				record = aspace.get(linked_record[0])
				record['linked_agents'].append(linked_agent)
				post_record = aspace.post(linked_record[0], record)
				posts.append(post_record)
			else:
				linked_agent = {'ref': survivor_aspace_record['uri'], 'role': linked_record[1], 'terms': [], 'relator': linked_record[2]}
				record = aspace.get(linked_record[0])
				record['linked_agents'].append(linked_agent)
				post_record = aspace.post(linked_record[0], record)
				posts.append(post_record)
		return posts

	except:
		logging.info('Updating failed for Linked Record {}'.format(linked_record[0]))
		return None


# for post in posts 
def cleanDupeAgentsFromLinkedRecords(post):
	''' Function to clean duplicate Agents from Linked Records'''

	uniq_agents = []
	record = aspace.get(post['uri'])
	for linked_agent in record['linked_agents']:
		if linked_agent not in uniq_agents:
			uniq_agents.append(linked_agent)

	record['linked_agents'] = uniq_agents

	post_record = aspace.post(post['uri'], record)

	return post_record


def testThatPostAgentsAreUnique(post):
	''' Function to test that post Agents are unique '''

	uniq_agents = []
	record = aspace.get(post['uri'])
	for linked_agent in record['linked_agents']:
		if linked_agent not in uniq_agents:
			uniq_agents.append(linked_agent)

	if len(uniq_agents) == len(record['linked_agents']):
		string ='Linked Agent test passed for Resource {}'.format(post['uri'])
		return string
	else:
		string = 'Linked Agent test failed for Resource {}'.format(post['uri'])
		return string


# Deleting Victim
def deleteVictim(victim_aspace_record):
	'''To be run after Survivor successfully updated with Victim's information'''
	delete = aspace.delete(victim_aspace_record['uri'])

	return delete


def reportStatus(dupe_aspace_record_set):
	'''Debugging tool to verify number of records and survivor values from ArchivesSpace record sets
	Returns number of records and their survivor status'''
	
	report = {}
	mythings = set()
	# Get list of keys for my report
	for records in record_sets['rows']:
		for record in records:
			mythings.add("%s" % record['live'])
	# Initialize values in report to 0
	for thing in mythings:
		report[thing] = 0
	for records in record_sets['rows']:
		for record in records:
			report["%s" % record['live']] += 1

	total = 0
	for thingtotal in report.keys():
		total = total + report[thingtotal]
		
	report['total'] = total
		
	return report


def countRecordSets(dupe_aspace_record_sets):
	"""Debugging tool to verify number of records and survivor values from ArchivesSpace record sets
	Returns number of records and their survivor status
	"""

	counter = len(dupe_aspace_record_sets['rows'])
	string = 'How many record sets: {}'.format(counter)
	
	return string

# fucked up the families

if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)


	# Write code for dupe sets with multiple survivors
	with open('linked_mult_dupe_aspace_records.txt') as jsonfile:
		try:
			record_sets = json.load(jsonfile)
		except ValueError:
			logging.info('File not found')
			exit(1)


	# Set counter
	dupe_count = 0

	# Initializing data transfer fail dictionary 
	transfer_fails = {}
	transfer_fails['rows'] = []

	# Initializing linked records fail dictionary
	errors = {}
	errors['rows'] = []

	for record_set in record_sets['rows']:
		survivor_set = getSurvivor(record_set)
	
		print('Before finalizing Survivor:')
		print(countLives(record_set))	
		print('\n')
	
		live_count = countLives(record_set)
		if 'True' in live_count.keys():
			if live_count['True'] == 1:
				pass
			elif live_count['True'] > 1:
				sole_survivor = determineSoleSurvivor(record_set)
			else:
				pass
		else:
			make_survivor = determineSurvivorForMultFalses(record_set)

		print('After finalizing Survivor:')
		print(countLives(record_set))
		print('\n')

		# Starting new Victim data field counter for each record set
		doe_counter = 0
		rel_agts_counter = 0
		notes_counter = 0
		names_counter = 0
		ext_doc_counter = 0
		agt_cont_counter = 0

		for record in record_set:			
			if record['live'] == False:
				try:	
					if len(record['dates_of_existence']) != 0:
						doe_counter += 1
				except:
					pass
				try:
					if len(record['related_agents']) != 0:
						rel_agts_counter += 1
				except:
					pass
				try:
					if len(record['notes']) != 0:
						notes_counter += 1
				except:
					pass
				try:
					if len(record['names']) != 0:
						names_counter += 1
				except:
					pass
				try:
					if len(record['external_documents']) != 0:
						ext_doc_counter += 1
				except:
					pass
				try:
					if len(record['agent_contacts']) != 0:
						agt_cont_counter += 1
				except:
					pass
	
		string = '''Victim counts before compiling data field dictionaries:\nDates of existence: {}, Related Agents: {}, Notes: {}, Names: {}, External Documents: {}, Agent Contacts: {}'''.format(doe_counter, rel_agts_counter, notes_counter, names_counter, ext_doc_counter, agt_cont_counter)
		print(string)


	# for record_set in record_sets['rows']:
		victim_records = []
		for record in record_set:
			if record['live'] == True:
				survivor = record
			else: 
				victim_records.append(record)

		# Get fresh copy of survivor
		survivor_record = aspace.get(survivor['uri'])
		survivor_uri = survivor_record['uri']

		v_dates = []
		v_notes = []
		v_acs = []
		v_exdocs = []
		v_ras = []
		v_names = []
		for victim in victim_records:
			victim_dates = getVictimDates(victim)
			if victim_dates != None:
				v_dates.append(victim_dates)
			victim_notes = getVictimNotes(victim)
			if victim_notes != None:
				v_notes.append(victim_notes)
			victim_agent_contacts = getVictimAgentContacts(victim)
			if victim_agent_contacts != None:
				v_acs.append(victim_agent_contacts)
			victim_exdocs = getVictimExternalDocuments(victim)
			if victim_exdocs != None:
				v_exdocs.append(victim_exdocs)
			victim_rel_agents = getVictimRelatedAgents(victim)
			if victim_rel_agents != None:
				v_ras.append(victim_rel_agents)
			victim_names = getVictimNameData(victim)
			if victim_names != None:
				v_names.append(victim_names)

		print('\n')
		print('Victim data fields after compiling data field dictionaries:')
		print('How many victim dates: {}'.format(len(v_dates)))
		print('How many victim notes: {}'.format(len(v_notes)))
		print('How many victim agent contacts: {}'.format(len(v_acs)))
		print('How many victim external documents: {}'.format(len(v_exdocs)))
		print('How many victim related agents: {}'.format(len(v_ras)))
		print('How many victim names: {}'.format(len(v_names)))

		# Giving victim data fields to survivor
		if len(v_dates) != 0:
			for dates in v_dates:
				survivor_record['dates_of_existence'].extend(dates)
		if len(v_notes) != 0:
			for note in v_notes:
				survivor_record['notes'].extend(note)
		if len(v_acs) != 0:
			for ac in v_acs:
				survivor_record['agent_contacts'].extend(ac)
		if len(v_exdocs) != 0:
			for exdoc in v_exdocs:
				survivor_record['external_documents'].extend(exdoc)
		if len(v_ras) != 0:
			for ra in v_ras:
				survivor_record['related_agents'].extend(ra)
		if len(v_names) != 0:
			for name in v_names:
				survivor_record['names'].extend(name)

		try:
			post_survivor = aspace.post(survivor_record['uri'], survivor_record)
			logging.info('\nPost successful: {}'.format(post_survivor['uri']))
		except:
			logging.info('\nPosting failed for {} {}'.format(survivor_record['title'], survivor_record['uri']))
			transfer_fails['rows'].append(record_set)


		# Linking Survivor Agent to Linked Records
		print('\n')
		print('Linking Survivor Agent to Records')
		record_count = 0
		# errors = {}
		# errors['rows'] = []
		set_with_linked_records = getLinkedAgentRoles(record_set)
		survivor_given_lrs = giveSurvivorLinkedRecords(set_with_linked_records)
		for record in survivor_given_lrs:
			if record['live'] == True:
				print('How many Survivor linked records before posting: {}'.format(len(record['linked_records'])))
				for linked_record in record['linked_records']:
					try:
						record_count += 1
						print(record_count)
						linkage = updateSurvivorsLinkedRecords(survivor_uri, linked_record)
						print(linkage)
						if 'FAIL!' in linkage:
							errors['rows'].append(linkage)
						else:
							cleaning = cleanDupeAgentsFromLinkedRecords(linkage)
							print('Cleaned any duplicate Agents from Record {}'.format(cleaning['uri']))
					except:
						logging.info('Failed: {}'.format(linked_record))
						errors['rows'].append(linked_record)

		print('\n')
		dupe_count += 1
		print('Repeat for next duplicate set....{}'.format(dupe_count))

	# Writing data field errors to a file
	with open('transfer_fails.txt', 'w') as outfile:
		json.dump(transfer_fails, outfile)

	# Writing linkage failures to a file
	with open('agent_attachment_fails.txt', 'w') as outfile:
		json.dump(errors, outfile)	

	
	# Deleting Victim Records
	with open('transfer_fails.txt') as json_file:
		try:
			transfer_fails = json.load(json_file)
		except ValueError:
			logging.info('Transfer fail file is empty')
			exit(1)


	# Compiling fails URIs so as not to delete those record sets
	fail_uris = []
	for record_set in transfer_fails['rows']:
		for record in record_set:
			if record['uri'] not in fail_uris:
				fail_uris.append(record['uri'])

	delete_fails = {}
	delete_fails['rows'] = []
	delete_count = 0
	for record_set in record_sets['rows']:
		for record in record_set:
			if record['live'] == False and record['uri'] not in fail_uris:
				try:
					delete = deleteVictim(record)
					delete_count += 1
					print(delete_count)
					print(delete)
				except:
					delete_fails['rows'].append(record)


	with open('deletion_fails.txt', 'w') as outfile:
		json.dump(delete_fails, outfile)


	print('''\n \n''')
	print('''Total Victims deleted {}'''.format(delete_count))
	print('''\n \n''')
	print('How many record_sets failed to transfer data: {}'.format(len(transfer_fails['rows'])))
	print('''\n \n''')	


