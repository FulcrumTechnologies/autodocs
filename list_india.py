#!/usr/bin/env python

"""list_india.py
Writes a page with listing of all environments with VPN connections to India.
"""

import commands
import json
import os

def write(names, ids, page_ids):
    """Write the page containing list of appropriate environments."""

    print ("Writing page.")

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
    space_key = config_data["wiki_space"]

    if os.path.isfile("other/india.json"):
        print("Page already exists. Replacing...")
        json_data = []

        # Make a JSON out of file info
        with open("other/india.json") as f:
            for line in f:
                json_data.append(json.loads(line))

        curl_cmd = ("curl -v -s -u " + username + ":" + password + " -X DELETE"
                    " " + location + str(json_data[0]["page_id"]) + " | python -m "
                    "json.tool > /dev/null")
        output = os.system(curl_cmd)

    page_name = "India VPN Environments"
    # parent_id here is the home page id for AutoDocs space.
    parent_id = "54362439"

    page_content = "<p>All environments that have a VPN connection to India will be listed below.</p>"
    for i in range(len(names)):
        page_content += "<p>"
        page_content += "<ac:link><ri:page ri:content-title=\\\"" + names[i] + "\\\" /><ac:plain-text-link-body><![CDATA[" + names[i] + " - {" + ids[i] + "}]]></ac:plain-text-link-body></ac:link>"
        page_content += "</p>"

    curl_cmd = ("curl -s -u " + username + ":" + password + " -X POST -H \'Content"
                "-Type: application/json\' -d\'{\"type\": \"page\",\"title\": "
                "\"" + page_name + "\",\"ancestors\": [{\"id\": "
                "" + parent_id + "}],\"space\": {\"key\": \"" + space_key + "\""
                "},\"body\": {\"storage\": {\"value\": \"" + page_content + "\""
                ",\"representation\": \"storage\"}}}\' " + location + " | "
                "python -mjson.tool > temp.json")

    output = os.system(curl_cmd)

    with open("temp.json") as file:
        data = json.load(file)

    # Empties temp.json
    open("temp.json", 'w').close()

    json_info = {}
    try:
        json_info["page_id"] = data["id"]
    except KeyError:
        print ("Something bad happened and the page apparently wasn't written.")

    env_details = []
    for i in range(len(names)):
        new_env = {}
        new_env["name"] = names[i]
        new_env["id"] = ids[i]
        new_env["page_id"] = page_ids[i]
        env_details.append(new_env)

    json_info["envs"] = env_details

    with open("other/india.json", "w") as file:
        json.dump(json_info, file)


def start(envs):
    """Starting point for list_india.py."""

    names = []
    ids = []
    page_ids = []

    json_dir = "JSONS/"

    count = 0

    for i in envs:
        count += 1
        print ("" + str(count) + ": checking " + i["name"] + "...")

        status, output = commands.getstatusoutput("python /opt/skynet/skynet.py"
                                                  " -a vms -e " + i["id"])
        data = json.loads(output)

        done = False

        for j in data["vms"]:
            try:
                for k in j["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"]:
                    if k["vpn_name"].startswith("SG"):

                        # Get page id
                        data = []
                        try:
                            with open(json_dir + i["id"] + ".json") as f:
                                for line in f:
                                    data.append(json.loads(line))
                        except IOError:
                            done = True
                            break

                        names.append(i["name"])
                        ids.append(i["id"])
                        page_ids.append(data[0]["page_id"])

                        done = True
                        break
            except KeyError:
                pass
            # If environment has been added to list, skip to next environment
            if done:
                break

    for x in range(len(names)):
        print ("ID: " + ids[x] + " - Page ID: " + page_ids[x] + " - Name: " + names[x])

    write(names, ids, page_ids)

