import json
import os
import os.path
import socket
import write_env
import write_vms

try:
    import requests
except ImportError:
    sys.stderr.write("You do not have the 'requests' module installed. "
                     "Please see http://docs.python-requests.org/en/latest/ "
                     "for more information.")
    exit(1)

# --------- Import yaml, then try to open config.yml -> store in list ---------

try:
    import yaml
except ImportError:
    sys.stderr.write("You do not have the 'yaml' module installed. " +
                     "Please see http://pyyaml.org/wiki/PyYAMLDocumentation " +
                     "for more information.")
    exit(1)

config_data = {}

try:
    f = open("config.yml")
    config_data = yaml.safe_load(f)
    f.close()
except IOError:
    sys.stderr.write("There is no config.yml in the directory. Create one " +
                     "and then try again.\nFor reference, check config_" +
                     "template.yml and follow the listed guidelines.\n")
    exit(1)

# ----------------- Store data from config in named variables -----------------

wiki_parent = config_data["wiki_parent"]

skytap_url = config_data["skytap_url"]
skytap_user = config_data["skytap_user"]
skytap_token = config_data["skytap_token"]

# --------------------- Request JSON for environment data ---------------------

requisite_headers = {'Accept': 'application/json',
                     'Content-Type': 'application/json'}
auth = (skytap_user, skytap_token)

response = requests.get(skytap_url + "/configurations/",
                        headers=requisite_headers, auth=auth)

env_data = json.loads(response.text)

# -------- Write specified amount of environments along with their vms --------

for i in range(2):
    if len(env_data[i]["error"]) is 0:
        response = requests.get(skytap_url + "/configurations/" + env_data[i]["id"],
                                headers=requisite_headers, auth=auth)
        envDetails = json.loads(response.text)

        envPageID, parentName = write_env.create(envDetails, wiki_parent)
        
	if envPageID != 999:
            write_vms.create(envDetails, envPageID, parentName)
