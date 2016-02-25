#!/usr/bin/env python

"""create_page.py

Initiate write_envs.py or write_vms.py depending on argument passed in. For
example, "python create_page.py env 5709327" will create a page for the
environment with ID 5709327, if such an environment exists.

This script is used exclusively by update.py.
"""

import commands
import json
import write_env
import write_vms
import skytap
import sys


def start(id, envs):
    """Start creation of page."""

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

    wiki_parent = config_data["wiki_parent"]

    # ------------- Take argv[1] ("env" or "vm") and argv[2] (ID) -------------

    env_details = envs[id]

    print ("Creating page for " + env_details.name + " ... ID: " + ""
           "" + str(env_details.id))
    env_page_id, parent_name = write_env.create(env_details, wiki_parent)

    if env_page_id != 0:
        write_vms.create(env_details, env_page_id, parent_name)

    return env_page_id


if __name__ == '__main__':
    start(sys.argv[1])

