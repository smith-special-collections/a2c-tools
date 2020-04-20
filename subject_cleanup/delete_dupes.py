from archivesspace import archivesspace
import argparse
import json
import logging
import pprint


def choose_victim(uri_tup):
	result = {}
	for uri in uri_tup:
		rec = aspace.get(uri)
		if rec['source'] == 'mesh':
			result['victim'] = rec['uri']
		else:
			result['survivor'] = rec['uri']

	return result


def force_hand(choose_victim_dict, uri_tup):
	if 'victim' not in choose_victim_dict.keys():
		choose_victim_dict['victim'] = ''

	for uri in uri_tup:
		if uri != choose_victim_dict['survivor']:
			choose_victim_dict['victim'] = uri

	return choose_victim_dict


def create_merge_dicts(uri_tup):
	first_round = choose_victim(uri_tup)
	second_round = force_hand(first_round, uri_tup)

	return second_round


def user_decides(merge_dict):
	victim = aspace.get(merge_dict['victim'])['title']
	survivor = aspace.get(merge_dict['survivor'])['title']

	decision = input(f'{victim} will be deleted and {survivor} will survive? Y or N? ')
	
	return decision


def format_request(merge_dict):
	d = merge_dict
	request = {}
	request['target'] = {}
	request['target']['ref'] = d['survivor']
	request['victims'] = []
	v = {}
	v['ref'] = d['victim']
	request['victims'].append(v)
	
	return request


if __name__ == '__main__':
	
	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	# argparser.add_argument("BAD_SUBDIVISIONS", nargs="+", help="Erroneous subdivisions")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)


	# bad_subdivisions = [bs.title() for bs in cliArguments.BAD_SUBDIVISIONS]


	with open('dupe_matches.json') as json_file:
		try:
			dupes = json.load(json_file)
		except:
			exit()
	
	# What am I trying to do?
	# If archival object source == mesh, that is the victim
	# If neither has a source == mesh, one at random is victim

	for count, dupe in enumerate(dupes['data'], 1):
		try:
			d = create_merge_dicts(dupe)
			decision = user_decides(d)
			if decision == 'y':
				request = format_request(d)
				merge = aspace.post('/merge_requests/subject', request)
				logging.info(merge['status'])
			elif decision == 'n':
				logging.info(f'Merge avoided. {d["survivor"]} and {d["victim"]} both remain.')
			else:
				logging.warning('Invalid response. Must by y or n.')
		except Exception as e:
			logging.error(e)



	print('\nAll dupes merged!')







