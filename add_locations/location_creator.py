from pprint import pprint as pp
from asnake.aspace import ASpace
import logging
import csv
import argparse
from datetime import datetime

START_DATE = datetime.today().strftime('%Y-%m-%d')

def create_location_instance(location_uri):
	instance = {'jsonmodel_type': 'container_location',
		  'ref': location_uri,
		  'start_date': START_DATE,
		  'status': 'current'}

	return instance

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description="Take CSV of locations uris and attach to corresponding top container")
	argparser.add_argument("CSV_FILE", help="CSV file of location data")
	cliargs = argparser.parse_args()

	aspace = ASpace()

	logging.basicConfig(level=logging.INFO)


	with open(cliargs.CSV_FILE) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			try:
				top_container = aspace.client.get(row['container_uri']).json()
				location_instance = create_location_instance(row['location_uri'])
				top_container['container_locations'] = []
				top_container['container_locations'].append(location_instance)
				post = aspace.client.post(row['container_uri'], json=top_container).json()
				logging.info(f'Location added to top container {row["container_uri"]}')
			except Exception as e:
				logging.error(f'{e}: {row["container_uri"]}')

