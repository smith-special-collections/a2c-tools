These are code files for creating new rare book resources.

- create_mrbc_agents.py creates new subjects and agents from a spreadsheet, like resource_template.csv.

- crosscheck_mrbc_agents_subs.py checks if the subjects and agents in the spreadsheet template already exist in ArchivesSpace. If not, create_mrbc_agents.py is run.

- make_mrbc_resources.py runs against the resource_template.csv with all necessary subject/agent uris in place to create new rare book resources.


Tested on Python 3.7.4. 
