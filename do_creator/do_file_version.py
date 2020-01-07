from archivesspace import archivesspace
import argparse
import json
import logging
import csv
import pprint


def create_file_version(fv_uri, fv_caption="", fv_id=""):
	'''Function to create data dict for new file version'''

	fv_dict = {'file_uri': fv_uri, 
		'publish': False, 
		'xlink_actuate_attribute': 'onRequest', 
		'xlink_show_attribute': 'new', 
		'jsonmodel_type': 'file_version', 
		'is_representative': False, 
		'identifier': fv_id,
		'caption': fv_caption}

	return fv_dict


def create_do(do_data, repo_num):
	'''Function to create do dicts for new dos'''
	if do_data['publish'].lower() == 'false':
		publish = False
	else:
		publish = True

	do_dict = {'dates': [],
		 'digital_object_id': do_data['digital_object_id'],
		 'extents': [],
		 'external_documents': [],
		 'external_ids': [],
		 'file_versions': [],
		 'is_slug_auto': False,
		 'jsonmodel_type': 'digital_object',
		 'language': 'eng',
		 'linked_agents': [],
		 'linked_events': [],
		 'linked_instances': [],
		 'notes': [],
		 'publish': publish,
		 'repository': {'ref': '/repositories/' + repo_num},
		 'restrictions': False,
		 'rights_statements': [],
		 'subjects': [],
		 'suppressed': False,
		 'title': do_data['digital_object_title']}

	return do_dict


def create_do_instance(successful_do_post):
	'''Function to link successfully created new do to archival object'''

	instance_dict = {'digital_object': {'ref': successful_do_post},
                'instance_type': 'digital_object',
                'is_representative': False,
                'jsonmodel_type': 'instance'}

	return instance_dict


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'recording'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("CSVFILE", default="DEFAULT", help="File path of csv file to pull digital object information from.")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)


	with open(cliArguments.CSVFILE, 'r') as file:
		reader = csv.DictReader(file)
		for row in reader:
			repo_num = row['uri'].split('/')[2]
			new_do = create_do(row, repo_num)
			if len(str(row['file_version_1_uri'])) != 0:
				new_file_version = create_file_version(row['file_version_1_uri'], row['file_version_1_caption'])
				new_do['file_versions'].append(new_file_version)
			if len(str(row['file_version_2_uri'])) != 0:
				new_file_version = create_file_version(row['file_version_2_uri'], row['file_version_2_caption'])
				new_do['file_versions'].append(new_file_version)
				
			# Creating digital object and linking it as an instance of its archival object
			try:
				create_digital_object = aspace.post('/repositories/' + repo_num + '/digital_objects', new_do)
				logging.info('Digital object creation successful! %s' % create_digital_object['uri'])
			except:
				logging.warning('Digital object creation failed. %s' % row['uri'])
				
			if create_digital_object:
				try:
					link = aspace.get(row['uri'])
					instance = create_do_instance(create_digital_object['uri'])
					link['instances'].append(instance)
					post_instance = aspace.post(link['uri'], link)
					logging.info('Successfully added digital object instance to %s' % post_instance['uri'])
				except:
					logging.warning('Failed to add digital object instance to %s' % link['uri'])





