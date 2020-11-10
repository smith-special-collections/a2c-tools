from asnake.aspace import ASpace
from pprint import pprint as pp
import csv
import argparse


if __name__ == '__main__':


	argparser = argparse.ArgumentParser()
	argparser.add_argument("CSVname", default="DEFAULT", help="Name of the CSV spreadsheet, e.g, 'duplaix.csv. Note: It must be in the same directory as this code file.")
	
	cliArguments = argparser.parse_args()

	csv_file = cliArguments.CSVname

	aspace = ASpace()

	with open(csv_file) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			record = aspace.client.get(f'/repositories/{row["repository"]}/archival_objects/{row["archival_object_id"]}').json()
			try:
				record['publish'] = True
				if len(record['notes']) > 0:
					for note in record['notes']:
						note['publish'] = True
				post = aspace.client.post(record['uri'], json=record)
				pp(post.json())
			except KeyError as e:
				pp(e)
