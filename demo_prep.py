
import json
import os
import os.path
import socket

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

skytap_url = config_data["skytap_url"]
skytap_user = config_data["skytap_user"]
skytap_token = config_data["skytap_token"]

# -----------------------------------------------------------------------------

requisite_headers = {'Accept': 'application/json',
                     'Content-Type': 'application/json'}
auth = (skytap_user, skytap_token)

response = requests.get(skytap_url + "/configurations",
                        headers=requisite_headers, auth=auth)
envs = json.loads(response.text)

x = 0

for i in envs:
    if len(i["error"]) is 0:
        with open("allSkytapIDs.txt", "a") as file:
            file.write(str(i["id"]) + "\n")

#print "There are " + str(x) + " valid environments"
#print response.text