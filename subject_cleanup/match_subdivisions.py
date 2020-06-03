import psycopg2
import json
import logging
from pprint import pprint as pp
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


	with open('phase_3_subs.json') as json_file:
		try:
			subs = json.load(json_file)
		except:
			logging.error('File not found')
			exit()


	matches = {}
	matches['rows'] = []
	for s in subs['RECORDS']:
		lst_s = s['sub_name'].split('--')
		m = {}
		m['uri'] = s['uri']
		m['unmatched'] = []
		m['matched'] = []
		for l in lst_s[:1]:
			try:
				if l[-1] == '.':
					l = l[:-1]
			except:
				continue

			match = cur.execute("SELECT * FROM subdivisions WHERE SIMILARITY(name, %s) > 0.9", (l.strip(),))
			match = cur.fetchone()
			if match != None:
				x = {}
				x['match'] = match[1]
				x['auth_id'] = match[0]
				x['smith_name'] = l
				m['matched'].append(x)
			else:
				m['unmatched'].append(l)

		matches['rows'].append(m)

				

	# Write to JSON
	with open('matched_complex_headings.json', 'w') as outfile:
		json.dump(matches, outfile)

	# # Write to CSV
	# with open('matched_subdivisions.csv', 'w', encoding='utf8', newline='') as output_file:
	#     f = csv.DictWriter(output_file, fieldnames=matches[0].keys(),)
	#     f.writeheader()
	#     f.writerows(matches)			




