from archivesspace import archivesspace
import argparse
import json
import logging
import csv
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


def getResourceTitle(repo, resource):
	resource = aspace.get('/repositories/' + str(repo) + '/resources/' + str(resource))
	resource_title = resource['title']

	return resource_title


if __name__ == "__main__":
	
	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("reponum", default="DEFAULT", help="Number of the repo to post to")
	argparser.add_argument("resourcenum", default="DEFAULT", help="Number of resource to disambiguate top containers for")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	repo = cliArguments.reponum
	resource = cliArguments.resourcenum

	resource_title = getResourceTitle(repo, resource)
	
	series = getSeries(repo, resource)

	# Gets data about Series level archival objects for a given Resource
	s_dicts = []
	for s in series:
		s_data = {}
		s_rec = aspace.get(s['record_uri'])
		s_data['create_time'] = s_rec['create_time'].split("T")[0] # Granular level is day, not day + time
		s_data['uri'] = s_rec['uri']
		s_data['title'] = s_rec['title']
		s_dicts.append(s_data)

	# Pulls out the most recently created Series
	for d in s_dicts:
		newest_series = d['create_time']
		if d['create_time'] > newest_series:
			newest_series = d['create_time']
	
	most_recent = []
	for d in s_dicts:
		if d['create_time'] == newest_series:
			most_recent.append(d)

	# Prints to console what the most recent Series are 
	print('-----------------------------')
	print(resource_title)
	print('-----------------------------')
	for count, i in enumerate(most_recent, 1):
		print(str(count) + ". " + i['title'] + " " + i['create_time'])

	print('-----------------------------')
	print('-----------------------------')

	# Accept the printed Series as most recent for program to continue, otherwise program will stop running
	question = input('These are the most recent series. Does this information look correct? Type y or n: ')
	if question.lower() == 'y' or question == 'yes':
		latest_series = []
		for i in most_recent:
			for s in series:
				if i['uri'] == s['record_uri']:
					series_uris = getChildUris(s)
					latest_series.extend(series_uris)
	else:
		logging.info('You selected no. Those were not the series you wanted.')
		exit()
	
	# pprint.pprint(latest_series)

	# Creates spreadsheet
	records = []
	for uri in latest_series:
		record_dict = {}
		record = aspace.get(uri)
		record_dict['resource'] = resource_title
		try:
			record_dict['title'] = record['title']
		except:
			record_dict['title'] = ""
		if not len(record['dates']) == 0:
			for date in record['dates']:
				try:
					record_dict['begin'] = date['begin']
				except:
					record_dict['begin'] = ""
		else:
			record_dict['begin'] = ""
		record_dict['file_version_1'] = ""
		record_dict['file_version_2'] = ""

		records.append(record_dict)


	with open('digital_object_template.csv', mode='w') as template:
		fieldnames = ['resource', 'title', 'begin', 'file_version_1', 'file_version_2']
		template_writer = csv.DictWriter(template, fieldnames=fieldnames)
		template_writer.writeheader()
		template_writer.writerows(records)

	logging.info('Spreadsheet complete!')

	template.close()






