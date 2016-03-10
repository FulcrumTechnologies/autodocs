#!/usr/bin/env python

"""update_write.py
Write wiki pages of environments which currently do not have said correlating
pages.
"""

import create_page
import json


def start(envs):
    """Write all remaining pages of environments not currently listed."""

    env_all = 0
    env_count = 0
    env_tried = 0
    env_written = 0

    try:
    	with open("allSkytapIDs.txt", "r") as f:
            id_list = [line.strip() for line in f]
    except IOError:
        id_list = []

    # Count up total so we have completetion dialogue (1/95, 2/95, etc.)
    for e in envs:
        if len(e.errors) is 0:
            if str(e.id) not in id_list:
                env_count += 1

    # Writing environments that are currently not in allSkytapIDs.txt
    for e in envs:
        env_all += 1
        if len(e.error) is 0:
            if str(e.id) not in id_list:
                env_tried += 1
                print ("(" + str(env_tried) + "/" + str(env_count) + ") Found "
                       "new environment. Name: " + e.name + " ... ID: "
                       "" + str(e.id))
                feedback = create_page.start(e)
                if feedback != 0:
                    env_written += 1

    print ("Total environments: " + str(env_count))
    print ("Environments tried: " + str(env_tried))
    print ("Environments written: " + str(env_written))
