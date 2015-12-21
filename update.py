#!/usr/bin/env python

"""update.py

Perform a check on current environments and vms and make changes to Confluence
page(s) if necessary. (As of 12/15, incomplete)
"""

import commands
import create_page
import json


def start():
    """Start the update function."""

    status, output = commands.getstatusoutput("python /opt/skynet/skynet.py -a "
                                              "env_full")

    envs = json.loads(output)

    env_count = 0
    env_tried = 0
    env_written = 0

    for i in envs:
        env_count += 1
        if len(i["error"]) is 0 and env_count < 7:
            env_tried += 1
            if i["id"] not in open('allSkytapIDs.txt').read():
                print ("Found new environment. Name: " + i["name"] + " ... ID: "
                       "" + i["id"])
                feedback = create_page.start(i["id"])
                if feedback != 0:
                    env_written += 1

    print ("Total environments: " + str(env_count))
    print ("Environments tried: " + str(env_tried))
    print ("Environments written: " + str(env_written))


if __name__ == '__main__':
    start()

