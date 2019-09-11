from archivesspace import archivesspace
import pprint
import argparse
import logging


if __name__ == "__main__":

	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("REPO", nargs="?", default="DEFAULT", help="Repository number")
	argparser.add_argument("RESOURCE_LIST", nargs="+", default="DEFAULT", help="List of resource numbers")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	repo_num = cliArguments.REPO
	resource_list = cliArguments.RESOURCE_LIST


	for count, resource_num in enumerate(resource_list, 1):
		print(count)
		logging.info('Checking agents for resource {}'.format(resource_num))
		try:
			resource = aspace.get('/repositories/' + repo_num + '/resources/' + resource_num)
			try:
				for agent in resource['linked_agents']:
					agent_record = aspace.get(agent['ref'])
					if agent_record['publish'] == False:
						agent_record['publish'] = True
						post = aspace.post(agent_record['uri'], agent_record)
						pprint.pprint(post)
					else:
						logging.info('Agent {} already published'.format(agent_record['uri']))
			except KeyError:
				logging.info('Error with agents for resource {}'.format(resource['title']))
		except:
			logging.info('Resource {} not found'.format(resource_num))
			pass

	# Checking that linked agents for resources are published
	for count, resource_num in enumerate(resource_list, 1):
		print(count)
		logging.info('Checking that agents are published for resource {}'.format(resource_num))
		try:
			resource = aspace.get('/repositories/' + repo_num + '/resources/' + resource_num)
			try:
				for agent in resource['linked_agents']:
					agent_record = aspace.get(agent['ref'])
					if agent_record['publish'] == True:
						pass
					else:
						logging.info('Agent {} is unpublished'.format(agent['uri']))
			except KeyError:
				logging.info('No agents for resource {}'.format(resource['title']))
		except:
			logging.info('Resource {} not found'.format(resource_num))
			pass
