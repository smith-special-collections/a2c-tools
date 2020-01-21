from archivesspace import archivesspace
import pprint
import argparse
import logging
import csv

def findKey(d, key):
    """Find all instances of key."""
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j


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

	
	logging.info('Getting all URIs for Resource {}'.format(resource))
	
	endpoint = '/repositories/' + repo + '/resources/' + resource + '/tree'
	output = aspace.get(endpoint)
	uris = []
	for value in findKey(output, 'record_uri'):
		if 'archival_objects' in value:
			uris.append(value)
	
	data = {}
	data['rows'] = []
	for uri in uris:
		record = aspace.get(uri)
		obj = getRecordInfo(record)
		data['rows'].append(obj)


	# Make spreadsheet	
	keys = data['rows'][1].keys()
	outpath = 'resource' + resource + '.csv'
	
	with open(outpath, 'w') as f:
		w = csv.DictWriter(f, keys)
		w.writeheader()
		for obj in data['rows']:
			w.writerow(obj)

	logging.info('Spreadsheet generated: {}'.format(outpath))


