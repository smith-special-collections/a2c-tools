import json
import logging
import csv
from pprint import pprint as pp
from asnake.aspace import ASpace
import urllib.parse
import requests
import argparse


def create_ext_doc(csv_match):
	ext_docs = []

	if len(csv_match['matched']) > 0:
		for m in csv_match['matched']:
			auth_id = m['match'] + '.html'
			ed = {'jsonmodel_type': 'external_document',
		            'location': auth_id,
		            'publish': False,
		            'title': m['smith_name'].strip()}
			ext_docs.append(ed)

	if len(csv_match['unmatched']) > 0:
		for um in csv_match['unmatched']: 
			ed = {'jsonmodel_type': 'external_document',
	            'location': f'This term was not matched to any valid Library of Congress subdivision.',
	            'publish': False,
	            'title': um.strip()}
			ext_docs.append(ed)
    
	return ext_docs    


def add_ext_doc_match(match):
	auth_id = match.headers['X-Uri'] + '.html'
	ed = {'jsonmodel_type': 'external_document',
		'location': auth_id,
		'publish': False,
		'title': match.headers['X-Preflabel']}
    
	return ed 


def add_ext_doc_unmatch(unmatch):
	ed = {'jsonmodel_type': 'external_document',
	    'location': f'This term was not matched to any valid Library of Congress subdivision.',
	    'publish': False,
	    'title': unmatch.strip()}

	return ed


if __name__ == "__main__":

	argparser = argparse.ArgumentParser()
	argparser.add_argument("FILE_NAME", nargs="+", default="DEFAULT", help="Name of JSON file of complex subjects to be matched")
	cliArguments = argparser.parse_args()

	logging.basicConfig(level=logging.INFO)
	aspace = ASpace()



	with open(cliArguments.FILE_NAME) as json_file:
		try:
			matches = json.load(json_file)
		except:
			logging.warning('File not found')
			exit()


	successes = 0
	fails = []
	for match in matches['rows'][10:]:
		sub_id = match['uri'].split('/')[-1]
		try:
			rec = aspace.subjects(sub_id).json()
		except Exception as e:
			logging.warning(e)

		if '--' in rec['title']: # Only concentrating on complex subjects	
			heading = rec['title'].split('--')[0].strip()
			heading = urllib.parse.quote(heading)
			query = 'http://id.loc.gov/authorities/subjects/label/' + heading
			r = requests.get(query)
			if r.status_code == 200:
				try:
					ext_doc = add_ext_doc_match(r)
					rec['external_documents'].append(ext_doc)
					to_be_first = rec['external_documents'].pop()
					rec['external_documents'].insert(0, to_be_first)
					successes += 1
					pp(successes)
					# pp(rec['title'])
					# pp(rec['external_documents'])
					# pp(rec['uri'])
					p = aspace.client.post(rec['uri'], json=rec).json()
					pp(p)

				except Exception as e:
					logging.warning(e)
					f = {'uri': match['uri'], 'title': rec['title']}
					fails.append(f)


			else:
				f = {'uri': match['uri'], 'title': rec['title']}
				fails.append(f)

	# pp(successes)
	# pp(len(fails))

	if len(fails) > 0:
		with open('second_ext_doc_fails.csv', 'w') as csv_file:
			writer = csv.DictWriter(csv_file, fieldnames=fails[0].keys(),)
			writer.writeheader()
			writer.writerows(fails)




