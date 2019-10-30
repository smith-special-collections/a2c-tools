from archivesspace import archivesspace
import argparse
import logging
import csv
import pprint


def add_extent_note(csv_field):
	note_dict = {'extent_type': 'HH:MM:SS_duration',
	  'jsonmodel_type': 'extent',
	  'number': csv_field,
	  'portion': 'whole'}

	return note_dict


def add_note(label, csv_field, note_type):
	note_dict =  {'jsonmodel_type': 'note_multipart',
	  'label': label,
	  'publish': True,
	  'subnotes': [{'content': csv_field,
	                'jsonmodel_type': 'note_text',
	                'publish': True}],
	  'type': note_type}

	return note_dict


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'recording'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVFILE", default="DEFAULT", help="Path to CSV file for parsing.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()


	with open(cliArguments.CSVFILE, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			record = aspace.get(row['archivalobject_uri'])
			if not len(str(row['extent1_containersummary'])) == 0: # Point 1 of email
				record['extents'][0]['container_summary'] = row['extent1_containersummary']
			if not len(str(row['extent1_physicaldetails'])) == 0:
				record['extents'][0]['physical_details'] = row['extent1_physicaldetails']
			if not len(str(row['duration'])) == 0: # Point 2 of email
				duration = add_extent_note(row['duration'])
				record['extents'].append(duration)
			if not len(str(row['edge_code_note'])) == 0: # Points 3 and 4 of email
				label = 'Edge code number'
				new_note = add_note(label, row['edge_code_note'], 'odd')
				record['notes'].append(new_note)
			if not len(str(row['box_label_note'])) == 0:
				label = 'Box label'
				new_note = add_note(label, row['box_label_note'], 'odd')
				record['notes'].append(new_note)
			if not len(str(row['phystech_note'])) == 0: # Point 5 of email -- will throw error because currently no field exists for it in your spreadsheet
				label = ""	
				new_note = add_note(label, row['phystech_note'], 'phystech')
				record['notes'].append(new_note)

			try:
				post = aspace.post(record['uri'], record)
				print('Successful update for {}'.format(post['uri']))
			except:
				print('Failed update for {}'.format(row['archivalobject_uri']))










