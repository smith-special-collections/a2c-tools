import psycopg2
import json
import logging
import pprint
import csv
import configparser

if __name__ == '__main__':

	fileName = 'pgsql.cfg'

	config = configparser.ConfigParser()
	config.read(fileName)
	config.sections()
	user = config['DEFAULT']['user']
	pw = config['DEFAULT']['password']

	conn = psycopg2.connect(f"dbname=LCSH user={user} password={pw}")
	cur = conn.cursor()

	# Excludes subjects with TGN/AAT as sources
	with open('all_subjects.json') as json_file:
		try:
			subs = json.load(json_file)
		except:
			logging.error('File not found')


	data = {}
	data['rows'] = []
	for sub in subs['RECORDS']:
		match = cur.execute("SELECT * FROM lcsh WHERE SIMILARITY(name, %s) > 0.9", (sub['name'],))
		match = cur.fetchone()
		if match != None:
			d = {}
			d['smith_name'] = sub['name']
			d['smith_uri'] = sub['uri']
			d['lcsh_name'] = match[0]
			d['lcsh_uri'] = match[1]
			d['lcsh_id'] = match[2]
			data['rows'].append(d)
			# print(sub['name'])
			# print(match)


	cur.close()
	conn.close()

	keys = data['rows'][0].keys()
	with open('lcsh_matches.csv', 'w') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=keys)
		writer.writeheader()
		for d in data['rows']:
			writer.writerow(d)



