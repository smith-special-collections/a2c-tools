from archivesspace import archivesspace
import pprint
import argparse
import logging
import csv


def getRecordInfo(aspace_record):
	obj = {}	
	
	try:
		obj['title'] = aspace_record['title']
	except:
		pass
	try:
		obj['level'] = aspace_record['level']
	except:
		pass
	# try:
	# 	obj['dates'] = aspace_record['dates']
	# except:
	# 	pass
	# try:
	# 	obj['publish'] = aspace_record['publish']
	# except:
	# 	pass
	try:
		obj['top_container'] = aspace_record['instances'][0]['sub_container']['top_container']['ref']
	except:
		obj['top_container'] = ""

	obj['uri'] = aspace_record['uri']

	return obj


def getSeries(resource_num, repo_num):
	'''Returns first level down children of given Resource'''

	logging.debug('Retrieving Series level children of Resource %s' % resource_num)
	series_lst = []

	record = aspace.get('/repositories/'+ str(repo_num) +'/resources/' + str(resource_num) + '/tree')

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


def getChildUris(series): 
	'''Returns list of child URIs for the child of a parent Resource. Assumes searching through a single series in a record group'''

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

	resource = aspace.get('/repositories/' + str(repo) + '/resources/' + str(resource_num))
	uri_lst = []
	uri_lst.append(resource['uri'])
	hierarchy = getSeries(resource_num, repo)
	for level in hierarchy:
		uri_lst.extend(getChildUris(level))

	return uri_lst


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("REPO", default="DEFAULT", help="Repository number")
	argparser.add_argument("RESOURCE", nargs="?", default="DEFAULT", help="Resource number")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	repo = cliArguments.REPO
	resource = cliArguments.RESOURCE


	# Get children info
	all_series = getSeries(resource, repo)
	logging.info('Getting all Series for Resource {}'.format(resource))
	
	count = 0
	ss_dicts = []
	for s in all_series:
		count += 1
		ss = {}
		ss[s['title']] = s
		ss_dicts.append(ss)
		print(count, ss.keys())
	

	series_num = input('Select number of the Series you would like: ')
	selected_series = ss_dicts[int(series_num) - 1]
	series = list(selected_series.values())[0]
	uris = getChildUris(series)

	data = {}
	data['rows'] = []
	for uri in uris:
		record = aspace.get(uri)
		obj = getRecordInfo(record)
		data['rows'].append(obj)


	# Make spreadsheet	
	keys = data['rows'][1].keys()
	outpath = 'resource' + resource + 'series' + series_num + '.csv'
	
	with open(outpath, 'w') as f:
		w = csv.DictWriter(f, keys)
		w.writeheader()
		for obj in data['rows']:
			w.writerow(obj)

	logging.info('Spreadsheet generated: {}'.format(outpath))


