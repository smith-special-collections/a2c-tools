from archivesspace import archivesspace
import argparse
import json
import logging
import pprint
import re


def remove_bad_subdivision(subject_terms, bad_subdivisions):
	''' Function searches through archivesspace record['terms'] and removes erroneous subdivisions '''
	for bs in bad_subdivisions:
		regex = "\s{0,2}" + "-{1,2}" + "\s{0,2}" + bs + "\.{0,1}"

		for term in subject_terms:
			if 'History and' not in term['term']:
				if re.search(regex, term['term']) != None:
					term['term'] = term['term'].replace(re.search(regex, term['term']).group(), "")			
			if bs == term['term'].strip():
				subject_terms.remove(term)

	return subject_terms


if __name__ == '__main__':
	
	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("BAD_SUBDIVISIONS", nargs="+", help="Erroneous subdivisions")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	# Bad subdivisions: History, Sources, Biography

	# Bad: African Americans -- History -- United States -- 20th century -- Sources
	# Good: African Americans--United States--20th century
	
	bad_subdivisions = [bs.title() for bs in cliArguments.BAD_SUBDIVISIONS]

	with open('subjects.json') as json_file:
		try:
			subs = json.load(json_file)
		except:
			logging.warning('File not found')
			exit()

	missed_subdivisions = {}
	missed_subdivisions['data'] = []

	fixed = {}
	fixed['data'] = []

	for count, k in enumerate(subs['rows'].keys(), 1):
		record = aspace.get(k)
		terms = remove_bad_subdivision(record['terms'], bad_subdivisions)
		record['terms'] = terms

		try:
			post = aspace.post(record['uri'], record)
			fixed['data'].append(post['uri'])
		except Exception as e:
			logging.warning(e)
			# Assigns temporary and unused source to prevent identical duplicates 
			# These will be deleted in another script
			record['source'] = 'mesh'
			try:
				post = aspace.post(record['uri'], record)
				fixed['data'].append(post['uri'])
			except Exception as e:
				logging.warning(e)
				missed_subdivisions['data'].append((record['title'], record['uri']))
		except Exception as e:
			logging.warning(e)
			missed_subdivisions['data'].append((record['title'], record['uri']))	
		

	print('Missed: ', len(missed_subdivisions['data']))	
	with open('missed_subdivisions.json', 'w') as outfile:
		json.dump(missed_subdivisions, outfile)
	
	print('Fixed: ', len(fixed['data']))
	with open('fixed.json', 'w') as outfile:
		json.dump(fixed, outfile)


