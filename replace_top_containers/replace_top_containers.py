from pprint import pprint as pp
from asnake.aspace import ASpace
import logging
import csv
import argparse


def create_top_container_instance(top_container_uri):
	instance = {'instance_type': 'mixed_materials',
	                'is_representative': False,
	                'jsonmodel_type': 'instance',
	                'sub_container': {'jsonmodel_type': 'sub_container',
	                                  'top_container': {'ref': top_container_uri}}}

	return instance


if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description="Create CA archival objects and top containers")
	argparser.add_argument("CSV_FILE", help="CSV file of archival object data to be created")
	cliargs = argparser.parse_args()

	aspace = ASpace()

	logging.basicConfig(level=logging.INFO)


	with open(cliargs.CSV_FILE, encoding='utf-8-sig') as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			ao = aspace.client.get(row['archival_object_uri']).json()
			top_container_instance = create_top_container_instance(row['top_container_uri'])
			if len(ao['instances']) > 0:
				for instance in ao['instances']:
					if instance['instance_type'] == 'mixed_materials':
						ao['instances'].remove(instance)
						ao['instances'].append(top_container_instance)
			else:
				ao['instances'].append(top_container_instance) 
			post = aspace.client.post(row['archival_object_uri'], json=ao).json()
			logging.info(f'Correct top container linked to {row["archival_object_uri"]}')


	# uri = aspace.client.get('/repositories/2/archival_objects/402326').json()
	# pp(uri)

