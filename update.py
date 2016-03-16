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
import sys


def reset(envs):
    """Reset every page in the wiki; utilized to update template."""

    json_dir = "JSONS/"
    for i in envs:
        if os.path.isfile(json_dir + i["id"] + ".json"):
            print ("Resetting environment " + i["name"] + " ... ID: " + i["id"])
            remove_page.start(i["id"])
            create_page.start(i["id"])


def purge():
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

        try:
            # [:-5] removes ".json" giving us the Skytap ID
            status, output = commands.getstatusoutput("python -W ignore::DeprecationWarning"
                                                      " /opt/skynet/skyne"
                                                      "t.py -a vms -e " + f[:-5])
            data = json.loads(output)
        except ValueError:
            print ("Removing page.")
            remove_page.start(env_data[0]["id"])


def get_json(skynet_arg):
    """Return json of output from a Skynet call."""

    if skynet_arg == "env_full":
        status, output = commands.getstatusoutput("python -W ignore::DeprecationWarning"
                                                  " /opt/skynet/skynet.py"
                                                  " -a env_full")

        envs = json.loads(output)
        return envs


def start(args):
    """Start the update function."""

    if (args[1] == "write"):
        os.system("clear")
        print ("Writing wiki pages.")
        envs = get_json("env_full")
        update_write.start(envs)
    elif (args[1] == "check"):
        os.system("clear")
        print ("Updating existing wiki pages.")
        envs = get_json("env_full")
        update_check.start(envs)
    elif (args[1] == "store"):
        os.system("clear")
        print ("Storing updated information from wiki pages.")
        envs = get_json("env_full")
        update_store.start(envs)
    elif (args[1] == "reset"):
        os.system("clear")
        print ("Resetting all wiki pages.")
        envs = get_json("env_full")
        reset(envs)
    elif (args[1] == "india"):
        os.system("clear")
        print ("Writing list of environments with VPN connections to India.")
        update_india.start()
    elif (args[1] == "purge"):
        os.system("clear")
        print ("Purging wiki pages that no longer have an environment.")
        purge()
    else:
        print ("Command not recognized.")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)
