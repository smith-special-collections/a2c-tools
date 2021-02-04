from pprint import pprint as pp
from asnake.aspace import ASpace
import logging
import csv
import argparse
import re
from datetime import datetime


START_DATE = datetime.today().strftime('%Y-%m-%d')

# {'jsonmodel_type': 'container_location',
# 	                          'ref': '',
# 	                          'status': 'current',
# 	                          'start_date': START_DATE}

def top_container_schema(row):
	if row['cp_uri'] != '/container_profiles/78':
		container_profile  = '/container_profiles/3'
	else:
		container_profile = row['cp_uri']


	top_container = {'active_restrictions': [],
	 'barcode': row['barcode'],
	 'collection': [],
	 'container_locations': [],
	 'container_profile': {'ref': container_profile},
	 'indicator': row['indicator'],
	 'jsonmodel_type': 'top_container',
	 'repository': {'ref': '/repositories/2'},
	 'restricted': False,
	 'type': row['type']}

	return top_container


def create_top_container_instance(top_container_uri):
	# instances = []
	instance = {'instance_type': 'mixed_materials',
	                'is_representative': False,
	                'jsonmodel_type': 'instance',
	                'sub_container': {'jsonmodel_type': 'sub_container',
	                                  'top_container': {'ref': top_container_uri}}}
	# instances.append(instance)

	return instance




if __name__ == "__main__":


	argparser = argparse.ArgumentParser(description="Create CA archival objects and top containers")
	argparser.add_argument("CSV_FILE", help="CSV file of archival object data to be created")
	cliargs = argparser.parse_args()

	aspace = ASpace()

	logging.basicConfig(level=logging.INFO)

	rows = []
	top_containers = []
	indicators = []
	with open(cliargs.CSV_FILE, encoding='utf-8-sig') as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			instance = {}
			if not row['indicator'] in indicators:
				indicators.append(row['indicator'])
				instance[row['indicator']] = top_container_schema(row)
				top_containers.append(instance)
			rows.append(row)


	
	tc_dict = {}
	for tc in top_containers:
		for k, v in tc.items():
			try:	
				post = aspace.client.post('/repositories/2/top_containers', json=v).json()
				pp(post)
				tc_dict[k] = create_top_container_instance(post['uri'])
			except Exception as e:
				logging.error(e)
	pp(tc_dict)

	for row in rows:
		try:
			record = aspace.client.get(row['ao_uri']).json()
			instance = tc_dict.get(row['indicator'])
			record['instances'].append(instance)
			post = aspace.client.post(row['ao_uri'], json=record).json()
			logging.info(f'Top container attached to AO {post["uri"]}')
		except KeyError:
			raise
		except Exception as e:
			logging.error(e)






	# 	count += 1
	# 	pp(count)
	# 	record = aspace.client.get(row['ao_uri']).json()
	# 	for tc in top_containers:
	# 		if row['indicator'] in tc.keys():
	# 			top_container_instance = create_top_container_instances(tc[row['indicator']]['uri'])
	# 			pp(top_container_instance)
	# 	record['instances'].append(top_container_instance)
	# 	pp(record['uri'])
	# 	pp(record['instances'])




	# pp(top_containers)





