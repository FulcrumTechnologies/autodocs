#!/usr/bin/env python

"""update.py
Contains calls to other scripts that perform various functions related to the
continuous updating of auto-documented wiki pages.
"""

import commands
import create_page
import json
import os
import remove_page
import update_check
import update_india
import update_store
import update_write
import skytap
import sys


def reset(envs):
    """Reset every page in the wiki; utilized to update template."""

    json_dir = "JSONS/"
    for e in envs:
        if os.path.isfile(json_dir + str(e.id) + ".json"):
            print ("Resetting environment " + e.name + " ... ID: " + str(e.id))
            remove_page.start(str(e.id))
            create_page.start(str(e.id))


def purge(envs):
    """Purge pages from wiki that no longer have a correlating environment."""
    json_dir = "JSONS/"
    count = 0

    print ("\nChecking for recently deleted environments...")
    for f in os.listdir(json_dir):
        env_data = []
        try:
            with open(json_dir + f) as file:
                for line in file:
                    env_data.append(json.loads(line))
        except IOError:
            print "This error should be impossible to achieve. Congratulations!"
            print "(Error found when trying to read JSON found in JSONS/ dir.)"
            continue

        try:
            if env_data[0]["parent_page_id"]:
                continue
        except (IndexError, KeyError):
            pass

        count += 1
        print ("" + str(count) + ": Trying " + env_data[0]["name"] + " with ID " + env_data[0]["id"])

        if f[:-5] not in envs:
            print ("Removing page.")
            remove_page.start(env_data[0]["id"])


def start(args):
    """Start the update function."""

    envs = skytap.Environments()

    if (args[1] == "write"):
        os.system("clear")
        print ("Writing wiki pages.")
        update_write.start(envs)
    elif (args[1] == "check"):
        os.system("clear")
        print ("Updating existing wiki pages.")
        update_check.start(envs)
    elif (args[1] == "store"):
        os.system("clear")
        print ("Storing updated information from wiki pages.")
        print ("Access denied. Which is just a fancy way of saying \"this is "
               "broken right now.\"")
        #update_store.start(envs)
    elif (args[1] == "reset"):
        os.system("clear")
        print ("Resetting all wiki pages.")
        reset(envs)
    elif (args[1] == "india"):
        os.system("clear")
        print ("Writing list of environments with VPN connections to India.")
        update_india.start()
    elif (args[1] == "purge"):
        os.system("clear")
        print ("Purging wiki pages that no longer have an environment.")
        purge(envs)
    else:
        print ("Command not recognized.")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)
