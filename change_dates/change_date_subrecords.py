from archivesspace import archivesspace
import pprint
import argparse
import logging


'**************************************'


def getSeries(resource_num, repo_num):
	"""Returns first level down children of given resource"""

	logging.debug('Retrieving Series level children of Resource %s' % resource_num)
	resource_num = str(resource_num)
	series_lst = []

	record = aspace.get('/repositories/'+ str(repo_num) +'/resources/' + resource_num + '/tree')

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
	'''Returns list of child URIs for the child of a parent resource. Assumes searching through a single series in a record group'''

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


def getAllResourceUris(resource_num, repo):
	'''Calls getSeries and getChildUris to return all the Archival Object URIs for a resource'''

	logging.info('Calling getSeries and getChildUris for Resource %s' % resource_num)
	hierarchy = getSeries(resource_num, repo)
	uri_lst = []
	for level in hierarchy:
		logging.info('Adding all Archival Object URIs for Resource to list')
		uri_lst.extend(getChildUris(level))

	return uri_lst


def change_date_type(archival_object):
	'''Function to change date type of an archival object from Other to Creation'''
	uri = archival_object['uri']

	try:
		archival_object['dates'][0]['label'] = 'creation'
		post_new_date_type = aspace.post(uri, archival_object)

		check = aspace.get(post_new_date_type['uri'])

		return check['dates'][0]['label']

	except:
		logging.info('Record would not update %s' % uri)
		return uri



if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("REPO", default="DEFAULT", help="Repository number")
	argparser.add_argument("RESOURCE_LIST", nargs="+", default="DEFAULT", help="Space delimited list of resource numbers")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	repo = cliArguments.REPO
	resource_lst = cliArguments.RESOURCE_LIST

	for resource in resource_lst:
		uris = getAllResourceUris(resource, repo)

		for uri in uris:
			archival_object = aspace.get(uri)
			try:
				if archival_object['dates'][0]['label'] == 'other':
					old_date_type = archival_object['dates'][0]['label']
					date_change = change_date_type(archival_object)
					print(old_date_type)
					print(date_change)
			except:
				logging.info('Did not change date for record %s' % archival_object['uri'])
				pass







