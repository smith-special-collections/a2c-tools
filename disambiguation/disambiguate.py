from archivesspace import archivesspace
import pprint
import argparse
import logging
import json
import csv
import string
import random


def randomString(stringLength=10):
    ' Function to generate a random string of fixed length '

    letters = string.ascii_lowercase
    
    return ''.join(random.choice(letters) for i in range(stringLength))


def makeNewContainer(box_num):
	' Function to make a new top container for Jill Ker Conway '

	string_1 = randomString()
	string_2 = randomString(4)
	new_cont = {'active_restrictions': [],
	 'barcode': string_1 + string_2,
	 'collection': [{'display_string': 'Office of the President Jill Ker Conway '
	                                   'Files',
	                 'identifier': 'CA--MS--00071',
	                 'ref': '/repositories/4/resources/374'}],
	 'container_locations': [],
	 'container_profile': {'ref': '/container_profiles/5'},
	 'indicator': str(box_num),
	 'jsonmodel_type': 'top_container',
	 'repository': {'ref': '/repositories/4'},
	 'restricted': False,
	 'series': [],
	 'type': 'box'}

	post = aspace.post('/repositories/4/top_containers', new_cont)

	return post['uri']


def getSeries(repo_num, resource_num):
	' Returns first level down children of given resource '

	logging.debug('Retrieving Series level children of Resource %s' % resource_num)
	series_lst = []

	record = aspace.get('/repositories/' + str(repo_num) + '/resources/' + str(resource_num) + '/tree')

	if record['children']:
		for child in record['children']:
			logging.debug('Adding each first level child of Resource %s to a list' % resource_num)
			series_lst.append(child)

	return series_lst


def getSeriesUri(series):
	return series['record_uri']


def getChildUri(child):
	logging.debug('Returning URI for Archival Object %s' % child['record_uri'])
	return child['record_uri']


def getChildUris(series):  # Could probably be reworked
	' Returns list of child URIs for the child of a parent resource '
	' Assumes searching through a single series in a record group '

	logging.debug('Retrieving URIs for each child of Series %s passed' % series)
	child_uris = []  # Starting list to append to
	children = series['children']  # Children of the series, which is itself the child of a record group

	child_uris.append(getSeriesUri(series))

	for child in children:
		child_uris.append(getChildUri(child))
		if child['children']:
			for child in child['children']:
				child_uris.append(getChildUri(child))
				if child['children']:
					for child in child['children']:
						child_uris.append(getChildUri(child))
						if child['children']:
							for child in child['children']:
								child_uris.append(getChildUri(child))
								if child['children']:
									for child in child['children']:
										child_uris.append(getChildUri(child))
										if child['children']:
											for child in child['children']:
												child_uris.append(getChildUri(child))
												if child['children']:
													for child in child['children']:
														child_uris.append(getChildUri(child))


	return child_uris




if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("reponum", nargs="?", default="DEFAULT", help="Number of the repo to post to")
	argparser.add_argument("resourcenum", nargs="?", default="DEFAULT", help="Number of resource to disambiguate top containers for")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	# Command line arguments
	repo_num = cliArguments.reponum
	resource_num = cliArguments.resourcenum

	# Gets series from resource tree
	series = getSeries(repo_num, resource_num)
	
	series_count = 0
	# Skips over the first series because assumes those top containers are correct
	for s in series[1:]: 
		series_count += 1
		print(series_count)
		# Gets the child uris for every series in the tree
		children = getChildUris(s) 
		# Starts dictionary for each child object
		series_dict = {} 
		for child in children:
			child_rec = aspace.get(child)
			try:
				uri = child_rec['uri']
				ref = child_rec['instances'][0]['sub_container']['top_container']['ref']
				box = aspace.get(ref)
				box_num = box['indicator']
				# Sets the key as the child object uri, the value as the box number
				series_dict[uri] = box_num 
			except:
				# Ignores file level objects without container instances
				pass 

		pprint.pprint(series_dict)

		# Pulls out the keys [uris]
		keys = series_dict.keys() 

		box_nums = []
		for k in keys:
			if series_dict[k] not in box_nums:
				# Adds the box numbers to a list to know how many boxes to create
				box_nums.append(series_dict[k]) 


		logging.info('How many box nums: {}'.format(len(box_nums)))

		new_cont_uris = []
		for num in box_nums:
			# Makes the new top container and adds the uri for it to a list
			new_cont = makeNewContainer(num) 
			new_cont_uris.append(new_cont)

		logging.info('How many new containers made: {}'.format(len(new_cont_uris)))

		new_cont_records = []
		for uri in new_cont_uris:
			# Grabs the ASpace record for each new container
			record = aspace.get(uri) 
			new_cont_records.append(record)

		logging.info('How many new container records retrieved: {}'.format(len(new_cont_records)))

		count = 0
		for k in keys:
			for cont in new_cont_records:
				# Verifies that the correct dummy box will be linked by matching the new box indicator to the old one, 
				# which is stored as the value for each key in the series dictionary
				if series_dict[k] == cont['indicator']: 
					count += 1
					print(count)
					record = aspace.get(k)
					record['instances'][0]['sub_container']['top_container']['ref'] = cont['uri']
					# Adds the new container link and updates the child record					
					post = aspace.post(k, record) 
					pprint.pprint(post)






