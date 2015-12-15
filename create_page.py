#!/usr/bin/env python

# -----------------------------------------------------------------------------
# create_page.py
#
# Initiate write_envs.py or write_vms.py depending on argument passed in. For
# example, "python create_page.py env 5709327" will create a page for the
# environment with ID 5709327, if such an environment exists.
#
# This script is used exclusively by update.py.
# -----------------------------------------------------------------------------

import json
import os
import os.path
import socket
import sys
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
    sys.stderr.write("You do not have the 'yaml' module installed. "
                     "Please see http://pyyaml.org/wiki/PyYAMLDocumentation "
                     "for more information.")
    exit(1)

config_data = {}

try:
    f = open("config.yml")
    config_data = yaml.safe_load(f)
    f.close()
except IOError:
    sys.stderr.write("There is no config.yml in the directory. Create one "
                     "and then try again.\nFor reference, check config_"
                     "template.yml and follow the listed guidelines.\n")
    exit(1)

# ----------------- Store data from config in named variables -----------------

wiki_parent = config_data["wiki_parent"]

skytap_url = config_data["skytap_url"]
skytap_user = config_data["skytap_user"]
skytap_token = config_data["skytap_token"]

# --------------- Take argv[1] ("env" or "vm") and argv[2] (ID) ---------------

try:
    print ("Creating " + sys.argv[1] + " with ID " + sys.argv[2])
except IndexError:
    print ("IndexError: you did not supply two arguments, ya dingus.")

if sys.argv[1] == "vm" or sys.argv[1] == "env":
    print ("Requesting Skytap services...")
    requisite_headers = {'Accept': 'application/json',
                         'Content-Type': 'application/json'}
    auth = (skytap_user, skytap_token)

if sys.argv[1] == "env":
    print ("Preparing to write...")
    response = requests.get(skytap_url + "/configurations/" + str(sys.argv[2]),
                            headers=requisite_headers, auth=auth)

    envDetails = json.loads(response.text)

    envPageID, parentName = write_env.create(envDetails, wiki_parent)

    if envPageID != 999:
        write_vms.create(envDetails, envPageID, parentName)

