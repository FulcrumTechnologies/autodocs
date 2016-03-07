#!/usr/bin/env python

"""update_india.py
Writes a page with listing of all environments with VPN connections to India.
"""

import commands
import json
import os
import remove_page


def content_unchanged(content, config_data):
    """Returns true if the content is no different than the last page's."""

    username = config_data["wiki_user"]
    password = config_data["wiki_pass"]

    json_data = []

    with open("other/india.json") as f:
        for line in f:
            json_data.append(json.loads(line))

    cmd = ("curl -u " + username + ":" + password + " https://fulcrumtech.atlassian.net/wiki/rest/api/content/" + json_data[0]["page_id"] + "?expand=body.storage > /tmp/temp.json")

    status, output = commands.getstatusoutput(cmd)

    with open("/tmp/temp.json") as file:
        page_data = json.load(file)

    content = content.replace("\\", "")

    return (content == page_data["body"]["storage"]["value"])


def write(names, ids, page_ids, content):
    """Write the page containing list of appropriate environments."""

    new_content = ""

    for i in range(len(names)):
        new_content += "<p>"
        new_content += "<ac:link><ri:page ri:content-title=\\\"" + names[i] + "\\\" /><ac:plain-text-link-body><![CDATA[" + names[i] + " - " + ids[i] + "]]></ac:plain-text-link-body></ac:link>"
        new_content += "</p>"

    if len(names) == 0:
        new_content += ("<p>No environments found. If you\'re seeing this, the "
                        "gobbledeegook has likely bunksmoogered, if you catch "
                        "my drift. Check update_india.py.</p>")

    return new_content


def make_page(content, config_data):
    """Call the Confluence Wiki API to delete the old page and create new."""
    print ("Writing page.")

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

    curl_cmd = ("curl -s -u " + username + ":" + password + " -X POST -H \'Content"
                "-Type: application/json\' -d\'{\"type\": \"page\",\"title\": "
                "\"" + page_name + "\",\"ancestors\": [{\"id\": "
                "" + parent_id + "}],\"space\": {\"key\": \"" + space_key + "\""
                "},\"body\": {\"storage\": {\"value\": \"" + content + "\""
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

    with open("other/india.json", "w") as file:
        json.dump(json_info, file)


def start():
    """Starting point for update_india.py."""

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

    names = []
    ids = []
    page_ids = []

    json_dir = "JSONS/"

    count = 0

    apac_names, apac_ids, apac_page_ids = [], [], []
    usw_names, usw_ids, usw_page_ids = [], [], []

    # Collecting data for APAC environments
    status, output = commands.getstatusoutput("python /opt/skynet/skynet.py"
                                              " -a vpn -e vpn-3288770")
    vpn = json.loads(output)

    for i in vpn["network_attachments"]:
        try:
            with open("" + json_dir + i["network"]["configuration_id"] + ".json") as file:
                data = json.load(file)
        except IOError:
            print "There\'s an environment missing. Run \"update.py write\"."
            continue

        print ("Adding (APAC): " + data["name"] + " with ID " + data["id"])

        apac_names.append(data["name"])
        apac_ids.append(data["id"])
        apac_page_ids.append(data["page_id"])

    # Collecting data for USW environments
    status, output = commands.getstatusoutput("python /opt/skynet/skynet.py"
                                              " -a vpn -e vpn-3631944")
    vpn = json.loads(output)

    for i in vpn["network_attachments"]:
        try:
            with open("" + json_dir + i["network"]["configuration_id"] + ".json") as file:
                data = json.load(file)
        except IOError:
            print "There\'s an environment missing (ID = " + i["network"]["configuration_id"] + ")."
            print "Run \"update.py write\"."
            continue

        print ("Adding (USW): " + data["name"] + " with ID " + data["id"])

        usw_names.append(data["name"])
        usw_ids.append(data["id"])
        usw_page_ids.append(data["page_id"])

    for x in range(len(apac_names)):
        print ("ID: " + apac_ids[x] + " - Page ID: " + apac_page_ids[x] + " - Name: " + apac_names[x])

    for x in range(len(usw_names)):
        print ("ID: " + usw_ids[x] + " - Page ID: " + usw_page_ids[x] + " - Name: " + usw_names[x])

    content = ""

    if len(apac_names) != 0:
        content += "<p>All APAC environments that have a VPN connection to India are listed below:</p>"
        content += write(apac_names, apac_ids, apac_page_ids, content)

    if len(usw_names) != 0:
        content += "<p>&nbsp;</p><p>All USW environments that have a VPN connection to India are listed below:</p>"
        content += write(usw_names, usw_ids, usw_page_ids, content)

    # Did anything change? If not, don't update page.
    if content_unchanged(content, config_data):
        print ("Nothing has changed; aborting update.")
        return

    make_page(content, config_data)
