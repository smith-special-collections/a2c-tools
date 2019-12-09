from archivesspace import archivesspace
import pprint
import argparse
import logging
import json

def check_for_note(aspace_record):
	checker = 0
	for note in record['notes']:
		try:
			if note['type'] == 'accessrestrict':
				if 'New Neilson' in note['subnotes'][0]['content']:
					checker += 1
		except:
			pass

	if checker > 1:
		pass
	else:
		return record


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("REPO_NUM", nargs="?", default=2, help="Repository number for CA (4), SSC (2), or MRBC (3)")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)


	repo_num = cliArguments.REPO_NUM


	resources = aspace.get('/repositories/' + str(repo_num) + '/resources?all_ids=true')

	note = "Until we move into New Neilson in early 2021, collections are stored in multiple locations and may take up to 48 hours to retrieve. Researchers are strongly encouraged to contact Special Collections (specialcollections@smith.edu) at least a week in advance of any planned visits so that boxes may be retrieved for them in a timely manner."

	new_conditions_note = {'jsonmodel_type': 'note_multipart',
  					'publish': True,
  					'rights_restriction': {'local_access_restriction_type': []},
  					'subnotes': [{'content': 'Until we move into New Neilson in early 2021, '
                           'collections are stored in multiple locations and '
                           'may take up to 48 hours to retrieve. Researchers '
                           'are strongly encouraged to contact Special '
                           'Collections (specialcollections@smith.edu) at '
                           'least a week in advance of any planned visits so '
                           'that boxes may be retrieved for them in a timely '
                           'manner.',
                	'jsonmodel_type': 'note_text',
                	'publish': True}],
  					'type': 'accessrestrict'}

	counter = 0
	fails = {}
	fails['rows'] = []
	for resource in resources:
		record = aspace.get('/repositories/' + str(repo_num) + '/resources/' + str(resource))
		check = check_for_note(record)
		if check != None:
			check['notes'].append(new_conditions_note)
			try:
				counter += 1
				update_record = aspace.post(record['uri'], record)
				logging.info('Finding aid for {} updated with new note'.format(record['title']))
			except:
				logging.warning('Note could not be added to finding aid for {}'.format(record['title']))
				fails['rows'].append(record['title'])
 
 
	print('How many Resources successfully had notes added {}'.format(counter))				
	print('How many Resources failed to update with new note: {}'.format(len(fails['rows'])))
	with open('manually_add_note.txt', 'w') as outfile:
		json.dump(fails, outfile)





