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


def start(args):
    """Start the update function."""

    status, output = commands.getstatusoutput("python /opt/skynet/skynet.py -a "
                                              "env_full")

    envs = json.loads(output)

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
        update_store.start(envs)
    elif (args[1] == "reset"):
        os.system("clear")
        print ("Resetting all wiki pages.")
        reset(envs)
    elif (args[1] == "india"):
        os.system("clear")
        print ("Writing list of environments with VPN connections to India.")
        update_india.start(envs)
    else:
        print ("Command not recognized.")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)

