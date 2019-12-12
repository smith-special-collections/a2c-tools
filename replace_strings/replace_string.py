from archivesspace import archivesspace
import argparse
import logging
import pprint


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


def getAllResourceUris(resource_num, repo_num):
	' Calls getSeries and getChildUris to return all the Archival Object URIs for a resource '
	
	resource_num = str(resource_num)
	repo_num = str(repo_num)
	
	logging.info('Calling getSeries and getChildUris for Resource %s' % resource_num)
	hierarchy = getSeries(resource_num, repo_num)
	uri_lst = []
	for level in hierarchy:
		logging.info('Adding all Archival Object URIs for Resource to list')
		uri_lst.extend(getChildUris(level))

	return uri_lst


def replace_quotes(key, replaced, replacer):
	''' Function to replace smart quotes in text with straight quotes '''

	key = key.replace(str(replaced), str(replacer))
	# key = key.replace("”", '"')

	return key


def get_all_keys(archive_space_record):
	''' Function to get all keys from a JSON archival object '''

	all_keys = []
	for key in archive_space_record.keys():
		all_keys.append(key)

	return all_keys



if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("reponum", default="DEFAULT", help="Number of the repo to post to")
	argparser.add_argument("resourcenum", default="DEFAULT", help="Number of resource to disambiguate top containers for")
	argparser.add_argument("wrongstring", default="DEFAULT", help="String to be replaced")
	argparser.add_argument("rightstring", default="DEFAULT", help="New string")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	replaced = cliArguments.wrongstring
	replacer = cliArguments.rightstring

	repo = cliArguments.reponum
	resource = cliArguments.resourcenum

	records = []
	record = aspace.get('/repositories/' + str(repo) + '/resources/' + str(resource))
	records.append(record)

	for record in records:
		keys = get_all_keys(record)
		pprint.pprint(keys)

		for count, key in enumerate(keys, 1):
			logging.info(count)
			if type(record[key]) == dict:
				logging.debug('Dictionary')
				next_keys = get_all_keys(record[key])
				for next_key in next_keys:
					if type(record[key][next_key]) == dict:
						third_keys = get_all_keys(record[key][next_key])
						for third_key in third_keys:
							try:
								record[key][next_key][third_key] = replace_quotes(record[key][next_key][third_key], replaced, replacer)
							except:
								if type(record[key][next_key][third_key]) == list:
									pass
								elif type(record[key][next_key][third_key]) == dict:
									pass
								else:
									pass
					elif type(record[key][next_key]) == list:
						for i in record[key][next_key]:
							third_keys = get_all_keys(i)
							for third_key in third_keys:
								try:
									i[third_key] = replace_quotes(i[third_key], replaced, replacer)
								except:
									if type(i[third_key]) == list:
										pass
									elif type(i[third_key]) == dict:
										pass
									else:
										pass
					else:
						try: 
							record[key][next_key] = replace_quotes(record[key][next_key], replaced, replacer)
						except:
							pass
			elif type(record[key]) == list:
				logging.debug('List')
				for i in record[key]:
					next_keys = get_all_keys(i)
					for next_key in next_keys:
						try:
							i[next_key] = replace_quotes(i[next_key], replaced, replacer)
						except:
							if type(i[next_key]) == dict:
								third_keys = get_all_keys(i[next_key])
								for third_key in third_keys:
									try:
										i[next_key][third_key] = replace_quotes(i[next_key][third_key], replaced, replacer)
									except:
										pass
							elif type(i[next_key]) == list:
								for x in i[next_key]:
									try:
										third_keys = get_all_keys(x)
										for third_key in third_keys:
											try:
												x[third_key] = replace_quotes(x[third_key], replaced, replacer)
											except:
												pass
									except:
										x = replace_quotes(x, replaced, replacer)
							else:
								pass
			else:
				logging.debug('Neither list nor dictionary')
				try:
					record[key] = replace_quotes(record[key], replaced, replacer)
				except:
					pass # type(test[key]) either 'bool' or 'int'


		post = aspace.post(record['uri'], record)
		print(post['uri'])

