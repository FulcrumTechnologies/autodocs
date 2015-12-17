#!/usr/bin/env python

"""purge_all_pages.py

Destroy all pages that have been written by Confluence Writer.
"""

import os


def start():
    """Start removal of all pages."""

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

    # ----- Read allPageIDs.txt line by line and delete appropriate pages -----

    output = "No pages to purge."

    with open("allPageIDs.txt", 'r') as file:
        for line in file:

            print ("\n\nDeleting page with ID: " + line)

            curl_cmd = ("curl -v -S -u " + username + ":" + password + " -X DELETE "
                        "" + location + str(line).rstrip('\n') + " | python -m "
                        "json.tool")
            output = os.system(curl_cmd)

    print (output)

    # Empties allPageIDs.txt
    open("allPageIDs.txt", 'w').close()

    # Empties allSkytapIDs.txt
    open("allSkytapIDs.txt", 'w').close()

    dir_path = "JSONS"
    file_list = os.listdir(dir_path)
    for file_name in file_list:
        os.remove(dir_path + "/" + file_name)


if __name__ == '__main__':
    start()
