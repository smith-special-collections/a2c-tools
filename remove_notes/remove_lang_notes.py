from archivesspace import archivesspace
import argparse
import logging
import pprint


if __name__ == '__main__':
	
	CONFIGFILE = "archivesspace.cfg"

	argparser = argparse.ArgumentParser()
	argparser.add_argument("SERVERCFG", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
	argparser.add_argument("REPO_NUMS", nargs="+", default="DEFAULT", help="Nums of repos, as list")
	cliArguments = argparser.parse_args()

	aspace = archivesspace.ArchivesSpace()
	aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
	aspace.connect()

	logging.basicConfig(level=logging.INFO)

	repos = cliArguments.REPO_NUMS

	# Key: finding_aid_language_note
	for repo in repos:
		resources = aspace.get(f'/repositories/{repo}/resources?all_ids=true')
		for resource in resources:
			try:
				rec = aspace.get(f'repositories/{repo}/resources/{resource}')
				if 'finding_aid_language_note' in rec.keys():
					if len(rec['finding_aid_language_note']) != 0:
						rec['finding_aid_language_note'] = ''
						try:
							post = aspace.post(rec['uri'], rec)
							logging.info(post['status'])
						except Exception as e:
							logging.error(e)
							continue
						
			except Exception as e:
				logging.error(e)
				continue


