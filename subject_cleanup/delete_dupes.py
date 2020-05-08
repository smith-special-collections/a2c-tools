from archivesspace import archivesspace
import argparse
import json
import logging
import pprint


def choose_victim(uri_tup):
	result = {}
	result['survivor'] = ''
	result['victim'] = ''
	for uri in uri_tup:
		rec = aspace.get(uri)
		if rec['source'] == 'lcsh':
			result['survivor'] = rec['uri']
		elif result['survivor'] == '':
			if rec['source'] == 'aat':
				result['survivor'] = rec['uri']
		elif result['survivor'] == '':
			if rec['source'] == 'tgn':
				result['survivor'] = rec['uri']
		else:
			result['victim'] = rec['uri']

	return result


def force_hand(choose_victim_dict, uri_tup):
	if choose_victim_dict['victim'] == '':
		for uri in uri_tup:
			if uri != choose_victim_dict['survivor']:
				choose_victim_dict['victim'] = uri

	if choose_victim_dict['survivor'] == '':
		for uri in uri_tup:
			if uri != choose_victim_dict['victim']:
				choose_victim_dict['survivor'] = uri

	if choose_victim_dict['survivor'] == '' and choose_victim_dict['victim'] == '':
		choose_victim_dict['survivor'] = uri_tup[0]
		choose_victim_dict['victim'] = uri_tup[1]

	return choose_victim_dict


def create_merge_dicts(uri_tup):
	first_round = choose_victim(uri_tup)
	second_round = force_hand(first_round, uri_tup)

	return second_round


def user_decides(merge_dict):
	victim_rec = aspace.get(merge_dict['victim'])
	victim = victim_rec['title']
	survivor_rec = aspace.get(merge_dict['survivor'])
	survivor = survivor_rec['title']
	print(victim_rec['source'], survivor_rec['source'])

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


def reverse_order(merge_dict):
	d = merge_dict
	n = {}
	n['victim'] = d['survivor']
	n['survivor'] = d['victim']

	return n


def merge(merge_dict):
	request = format_request(merge_dict)
	merge = aspace.post('/merge_requests/subject', request)
	logging.info(merge['status'])


def delete(dupe):
	try:
		d = create_merge_dicts(dupe)
		decision = user_decides(d)
		if decision == 'y':
			merge(d)
		elif decision == 'n':
			print('Do you wish to have the order reversed? Y or n.')
			answer = input()
			if answer == 'y':
				n = reverse_order(d)
				merge(n)
			else:
				logging.info(f'Merge avoided. {d["survivor"]} and {d["victim"]} both remain.')
		else:
			logging.warning('Invalid response. Must by y or n.')
			restart = input('Try again? Y or n. ')
			if restart == 'y':
				logging.info(f'{d["victim"]} successfully merged with {d["survivor"]}.')
				merge(d)
			else:
				exit()
	except Exception as e:
		logging.error(e)



if __name__ == '__main__':
	
	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("JSONFILE", default="DEFAULT", help="Name and path of JSON file containing dupe pairs")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	jf = cliArguments.JSONFILE
	with open(jf) as json_file:
		try:
			dupes = json.load(json_file)
		except:
			exit()
	
	count = 0
	for dupe in dupes['rows']:
		count += 1
		print(count)
		delete(dupe)


	print('\nAll dupes merged!')










