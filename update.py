#!/usr/bin/env python

"""update.py
Perform a check on current environments and vms and make changes to Confluence
page(s) if necessary. (As of 12/15, incomplete)
"""

import commands
import create_page
import json
import os
import remove_page
import sys


def write(envs):
    """Write all remaining pages of environments not currently listed."""

    env_all = 0
    env_count = 0
    env_tried = 0
    env_written = 0

    with open("allSkytapIDs.txt", "r") as f:
        id_list = [line.strip() for line in f]

    # Count up total so we have completetion dialogue (1/95, 2/95, etc.)
    for i in envs:
        if len(i["error"]) is 0:
            if str(i["id"]) not in id_list:
                env_count += 1

    # Writing environments that are currently not in allSkytapIDs.txt
    for i in envs:
        env_all += 1
        if len(i["error"]) is 0:
            if str(i["id"]) not in id_list:
                env_tried += 1
                print ("(" + str(env_tried) + "/" + str(env_count) + ") Found new"
                       " environment. Name: " + i["name"] + " ... ID: " + i["id"])
                feedback = create_page.start(i["id"])
                if feedback != 0:
                    env_written += 1

    print ("Total environments: " + str(env_count))
    print ("Environments tried: " + str(env_tried))
    print ("Environments written: " + str(env_written))


def check_and_rewrite(envs):
    """Check for differences between page and current env JSON, and update."""

    json_dir = "JSONS/"

    count = 0

    # listed_envs is used in a special case scenario where env is deleted
    # from Skytap. The page will be removed along with its vms.
    listed_envs = []

    for i in envs:
        listed_envs.append(i["id"])
        count += 1

        print ("\n----------------------------------------\n")
        print ("Environment " + str(count) + ": " + i["name"] + " ... ID: " + i["id"])

        # Get JSON matching environment ID
        if os.path.isfile(json_dir + i["id"] + ".json"):
            print ("Collecting environment data..."),
            data = []

            # Make a JSON out of file info
            with open(json_dir + i["id"] + ".json") as f:
                for line in f:
                    data.append(json.loads(line))

            status, output = commands.getstatusoutput("python /opt/skynet/skynet.py"
                                                      " -a vms -e " + i["id"])

            cur_data = json.loads(output)

            print ("checking for changes..."),
            # NOTE: this list of things to compare is incomplete. Refer to JSON
            # of environments in /JSONS to get full list of elements to compare.
            if (data[0]["config_url"] != cur_data["url"] or
                    data[0]["id"] != cur_data["id"] or
                    data[0]["name"] != cur_data["name"]):
                    # Environment data has been changed; update.
                    print ("changes found.")
                    print ("Update: environment data has been altered.")
                    print ("Changes found in: " + data[0]["name"] + "... ID: "
                           "" + data[0]["id"])
                    remove_page.start(data[0]["id"])
                    create_page.start(data[0]["id"])
                    continue
            else:
                print ("no changes found.")
            # listed_vms is used in a special case scenario where vm is deleted
            # from an environment. The page will be removed if vm is removed.
            listed_vms = []

            for i in data[0]["vms"]:
                listed_vms.append(i["vm_id"])

            vm_count = 0
            # Check all of the environment's vms.
            for i in cur_data["vms"]:
                vm_count += 1
                print ("\nVM " + str(vm_count) + ": " + i["name"] + " ... ID: " + i["id"])
                if os.path.isfile(json_dir + i["id"] + ".json"):
                    print ("Collecting VM data..."),
                    vm_data = []

                    try:
                        # Make a JSON of vm file info
                        with open(json_dir + i["id"] + ".json") as f:
                            for line in f:
                                vm_data.append(json.loads(line))

                        print ("checking for changes..."),
                        if (vm_data[0]["id"] != i["id"] or
                                vm_data[0]["local_ip"] != i["interfaces"][0]["ip"] or
                                vm_data[0]["vm_name"] != i["name"] or
                                vm_data[0]["config_url"] != i["configuration_url"] or
                                vm_data[0]["vm_hostname"] != i["interfaces"][0]["hostname"]):
                                # Vm data has been changed; update.
                                print ("changes found.")
                                print ("Update: VM data has been altered.")
                                print ("Changes found in: " + data[0]["name"] + ""
                                       "... ID: " + data[0]["id"] + "... VM: "
                                       "" + vm_data[0]["vm_name"] + "... ID: "
                                       "" + vm_data[0]["id"] + "\n\n")
                                remove_page.start(data[0]["id"])
                                create_page.start(data[0]["id"])
                                continue
                    except FileNotFoundError:
                        # Another vm has been added to the environment; update.
                        print ("no data found.")
                        print ("Update: VM has been added to environment.")
                        print ("Changes found in: " + data[0]["name"] + "... ID: "
                               "" + data[0]["id"])
                        remove_page.start(data[0]["id"])
                        create_page.start(data[0]["id"])
                        continue

                # Remove from listed_vms if this vm still exists.
                if i["id"] in listed_vms:
                    listed_vms.remove(i["id"])

            print ("\nChecking for recently deleted VMs..."),
            # If there are still elements in listed_vm...
            if len(listed_vms) != 0:
                # One or more vms have been removed from environment; update.
                print ("orphaned vm data found. We\'ll code-name it \"Bruce Wayne\".")
                print ("Update: environment has been shot dead in front of Bruce Wayne.")
                print ("Changes found in: " + data[0]["name"] + "... ID: "
                       "" + data[0]["id"] + " ... Cave: of the Bat variety.")
                remove_page.start(data[0]["id"])
                create_page.start(data[0]["id"])
                continue
            else:
                print ("no orphaned VMs found.")

    # Check every file representing an environment from the JSONS directory
    # against each ID in listed_envs. If not found, call remove_page for that
    # ID. This ensures envs that were removed will have their pages purged too.
    print ("\nChecking for recently deleted environments...")
    for f in os.listdir(json_dir):
        env_data = []
        with open(json_dir + f) as f:
            for line in f:
                env_data.append(json.loads(line))

        try:
            # If this JSON belongs to environment and id is not in listed_envs
            if env_data[0]["vms"] and env_data[0]["id"] not in listed_envs:
                print ("deleted environment found...or, rather, it hasn\'t?")
                print ("Update: Environment has been deleted.")
                print ("Changes found in: " + env_data[0]["name"] + "... ID: "
                       "" + env_data[0]["id"])
                remove_page.start(env_data[0]["id"])
                continue
        except (IndexError, KeyError):
            pass

    print ("\n\nJob\'s done.\n")


def start(args):
    """Start the update function."""

    status, output = commands.getstatusoutput("python /opt/skynet/skynet.py -a "
                                              "env_full")

    envs = json.loads(output)

    if (args[1] == "write"):
        print "Writing environments."
        write(envs)

    if (args[1] == "check"):
        print "Updating existing environments."
        check_and_rewrite(envs)


if __name__ == '__main__':
    start(sys.argv)

