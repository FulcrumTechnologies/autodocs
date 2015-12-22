#!/usr/bin/env python

"""remove_page.py

Remove one page. Call this method with "python remove_page.py [env/vm ID]".
Vm pages will be removed normally, but environment pages will be removed along
with all child pages (vm pages).
"""

import json
import os
import os.path
import sys


def remove(username, password, location, data, path):
    """Delete page, along with references in JSONS/ and allPageIDs.txt."""

    print "\n\nDeleting page with Skytap ID: " + str(data[0]["id"])

    curl_cmd = ("curl -v -S -u " + username + ":" + password + " -X DELETE"
                " " + location + str(data[0]["page_id"]) + " | python -m "
                "json.tool")
    output = os.system(curl_cmd)
    print (output)

    # Delete instance from allPageIDs.txt
    f = open("allPageIDs.txt", "r")
    lines = f.readlines()
    f.close()

    f = open("allPageIDs.txt", "w")
    for line in lines:
        if str(data[0]["page_id"]) not in line:
            f.write(line)

    # Delete instance from allSkytapIDs.txt
    f = open("allSkytapIDs.txt", "r")
    lines = f.readlines()
    f.close()

    f = open("allSkytapIDs.txt", "w")
    for line in lines:
        if str(data[0]["id"]) not in line:
            f.write(line)

    f.close()

    # Delete instance from JSONS directory
    os.system("rm -f " + path + str(data[0]["id"]) + ".json")


def remove_env(username, password, location, data, path):
    """Removes all vms associated with environment, then removes environment."""

    for i in data[0]["vms"]:
        try:
            vm_data = []

            with open(path + str(i["vm_id"]) + ".json") as f:
                for line in f:
                    vm_data.append(json.loads(line))

            remove(username, password, location, vm_data, path)
        except IOError:
            print "Missed a vm? Something went wonky!"

    # This call will finally remove the environment.
    remove(username, password, location, data, path)


def start(id):
    """Start removal of page."""

    # ------- Import yaml, then try to open config.yml -> store in list -------

    try:
        import yaml
    except ImportError:
        sys.stderr.write("You do not have the 'yaml' module installed. "
                         "Please see http://pyyaml.org/wiki/PyYAMLDocumentation"
                         " for more information.")
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

    # --------------- Store data from config in named variables ---------------

    username = config_data["wiki_user"]
    password = config_data["wiki_pass"]
    location = config_data["wiki_url"]

    # --- Take arg from command line (must be environment or vm) and delete ---

    path = "JSONS/"

    file_name = path + str(id) + ".json"

    if os.path.isfile(file_name):
        data = []

        # Make a JSON out of file info
        with open(file_name) as f:
            for line in f:
                data.append(json.loads(line))

        remove_env(username, password, location, data, path)


if __name__ == '__main__':
    start(0)

