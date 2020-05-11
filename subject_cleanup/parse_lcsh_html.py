import argparse
import logging
import csv
import pprint
from bs4 import BeautifulSoup
import requests
import json


def translate_term_type(html_term):
	'''Translates term type from LoC HTML into ASpace recognized value'''
	if html_term == 'Topic' or html_term == 'Topic Component':
		term_type = 'topical'
	elif html_term == 'Geographic' or html_term == 'Geographic Component':
		term_type = 'geographic'
	elif html_term == 'GenreForm' or html_term == 'GenreForm Component':
		term_type = 'genre_form'
	elif html_term == 'Temporal' or html_term == 'Temporal Component':
		term_type = 'temporal'
	elif html_term == 'CorporateName' or html_term == 'CorporateName Component':
		term_type = 'corporate_name'
	else:
		term_type = html_term

	return term_type
 


if __name__ == "__main__":

	logging.basicConfig(level=logging.INFO)

	component_list = {}
	component_list['rows'] = []
	
	with open('lcsh_matches.csv') as csv_file:
		reader = csv.DictReader(csv_file)

		for match in reader:
			url = match['lcsh_uri'] + '.html' #http://id.loc.gov/authorities/subjects/sh2008120376.html
			page = requests.get(url)
			soup = BeautifulSoup(page.text, 'html.parser')

			subject = {}
			subject['name'] = match['lcsh_name']
			subject['uri'] = match['lcsh_uri']
			subject['auth_id'] = match['lcsh_id']
			subject['smith_uri'] = match['smith_uri']
			subject['components'] = []

			if '--' in match['lcsh_name']: 
				components = soup.find(rel='madsrdf:componentList')

				try:
					component_items = components.find_all('li')
					for component in component_items:
						component_dict = {}
						img = component.find('img') # img tag
						a_href = component.find('a') # a href tag
							
						try:
							component_dict['term'] = a_href.contents[0]
						except:
							span = component.find('span')
							if span != None:
								component_dict['term'] = span.contents[0]							
						
						try:
							term_type = translate_term_type(img['title'])
							component_dict['term_type'] = term_type
						except:
							component_dict['term_type'] = ''

						subject['components'].append(component_dict)

				except Exception as e:
					logging.error(e)
					continue

			else:
				typ = soup.find(property='rdf:type')
				component_dict = {}
				component_dict['term'] = match['lcsh_name']
				html_term = typ.contents[0].split(' ')[1] 
				term_type = translate_term_type(html_term)
				component_dict['term_type'] = term_type
				
				subject['components'].append(component_dict)
				
			component_list['rows'].append(subject)

	pprint.pprint(component_list['rows'])
	print(len(component_list['rows']))

	with open('matched_subjects_with_term_types.json', 'w') as outfile:
		json.dump(component_list, outfile)




