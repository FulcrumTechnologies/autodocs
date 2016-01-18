#!/usr/bin/env python

"""update_store.py
Stores information from fields denoted by an asterisk * on wiki pages. This info
is stored in a JSON in the "storage" directory.
"""

import json
import os
import sys


def start(envs):
    """Store specific data from pages to preserve through future updates."""

    try:
        import yaml
    except ImportError:
        sys.stderr.write("You do not have the 'yaml' module installed. "
                         "Please see http://pyyaml.org/wiki/PyYAMLDocumentation"
                         " for more information.")
        exit(1)

    try:
        f = open("config.yml")
        config_data = yaml.safe_load(f)
        f.close()
    except IOError:
        sys.stderr.write("There is no config.yml in the directory. Create one "
                         "and then try again.\nFor reference, check config_"
                         "template.yml and follow the listed guidelines.\n")
        exit(1)

    location = config_data["wiki_url"]
    username = config_data["wiki_user"]
    password = config_data["wiki_pass"]

    json_dir = "JSONS/"
    storage_dir = "storage/"

    for i in envs:
        # Get JSON matching environment ID
        if os.path.isfile(json_dir + i["id"] + ".json"):
            print ("Storing data of " + i["name"] + " ... ID: " + i["id"])
            print ("Collecting environment data..."),
            data = []

            # Make a JSON out of file info
            with open(json_dir + i["id"] + ".json") as f:
                for line in f:
                    data.append(json.loads(line))

            print ("fetching page source..."),
            curl_cmd = ("curl -s -u " + username + ":" + password + " "
                        "" + location + data[0]["page_id"] + "?expand=body.stor"
                        "age | python -mjson.tool > temp.json")

            output = os.system(curl_cmd)

            with open("temp.json") as file:
                result = json.load(file)

            # Empties temp.json
            open("temp.json", 'w').close()

            storage_info = {}
            content = result["body"]["storage"]["value"]

            # NOTE: this is where the magic happens. Add elements here.
            print ("storing relevant information in JSON..."),
            storage_info["comment"] = content[content.find("<ac:layout-cell><p>")+19:content.find("</p></ac:layout-cell>")]
            storage_info["user"] = content[content.find("Admin User*:")+12:content.find("</p><p>Admin PW")].strip()
            storage_info["password"] = content[content.find("Admin PW*:")+10:content.find("</p><p>Skytap Environment")].strip()
            storage_info["mob_ver"] = content[content.find("Version*:")+9:content.find("</p><p>APK Build")].strip()
            storage_info["apk_build"] = content[content.find("APK Build*:")+11:content.find("</p><p>WAR Build")].strip()
            storage_info["war_build"] = "?" #content[content.find("WAR Build*:")+11:content.find("</p><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><table>")]

            with open(storage_dir + i["id"] + ".json", "w") as file:
                json.dump(storage_info, file)

            print ("done.\n")

