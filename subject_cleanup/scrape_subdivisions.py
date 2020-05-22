import argparse
import csv
import logging
from pprint import pprint as pp
import requests
from bs4 import BeautifulSoup


def get_next_query(soup):
	next_url = soup.find_all('a', {"class": "next"})
	next_q = next_url[0].attrs['href']
	next_url = 'http://id.loc.gov/search/' + next_q
	
	if 'collection_Subdivisions' in next_url:
		return next_url
	else:
		return None


def get_subdivisions_from_html(soup):	
	sub_lst = []
	tbody = soup.tbody
	for child in tbody.children:
		a_tag = child.find('a')
		if type(a_tag) != int:
			sub = {}
			sub['auth_id'] = 'http://id.loc.gov' + a_tag.attrs['href']
			sub['name'] = a_tag.contents[0]
			sub_lst.append(sub)

	return sub_lst




if __name__ == "__main__":

	logging.basicConfig(level=logging.INFO)


	starting_url = 'http://id.loc.gov/search/?q=memberOf:http://id.loc.gov/authorities/subjects/collection_Subdivisions&start=1'
	first_req = requests.get(starting_url).text

	soup = BeautifulSoup(first_req, 'html.parser')	
	
	subs = get_subdivisions_from_html(soup)
	next_url = get_next_query(soup)
	
	subdivisions = []
	subdivisions.extend(subs)
	
	while next_url != None:
		r = requests.get(next_url).text
		soup = BeautifulSoup(r, 'html.parser')
		subs = get_subdivisions_from_html(soup)
		if len(subs) != 0:
			subdivisions.extend(subs)
		next_url = get_next_query(soup)

	
	# Write to CSV
	with open('lc_subdivisions.csv', 'w', encoding='utf8', newline='') as output_file:
	    fc = csv.DictWriter(output_file, fieldnames=subdivisions[0].keys(),)
	    fc.writeheader()
	    fc.writerows(subdivisions)


