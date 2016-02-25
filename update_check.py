#!/usr/bin/env python

"""update_check.py
Updates environment/VM pages upon finding discrepancies between real-time info
and already-written info.
"""

import commands
import create_page
import json
import os
import remove_page


def clean_string(str):
    """Clean up lone apostrophes and quotations in string."""
    str = str.replace("\'", "")

    return str


def start(envs):
    """Check for differences between page and current env JSON, and update."""

    json_dir = "JSONS/"

    count = 0

    for i in envs:
        count += 1

        print ("\n----------------------------------------\n")
        print ("Environment " + str(count) + ": " + i.name + " ... ID: " + str(i.id))

        # Get JSON matching environment ID
        if os.path.isfile(json_dir + str(i.id) + ".json"):
            changes_made = False
            print ("Collecting environment data..."),
            data = []

            # Make a JSON out of file info
            with open(json_dir + str(i.id) + ".json") as f:
                for line in f:
                    data.append(json.loads(line))

            # cur_data is the up-to-date list of vms in environment
            cur_data = envs[i.id]

            print ("checking for changes..."),
            # NOTE: this list of things to compare is incomplete. Refer to JSON
            # of environments in /JSONS to get full list of elements to compare.
            if (data[0]["config_url"] != cur_data.url or
                    data[0]["id"] != str(cur_data.id) or
                    data[0]["name"] != clean_string(cur_data.name)):
                    print ("" + data[0]["config_url"] + " - " + cur_data.url)
                    print ("" + data[0]["id"] + " - " + str(cur_data.id))
                    print ("" + data[0]["name"] + " - " + cur_data.name)
                    # Environment data has been changed; update.
                    print ("changes found.")
                    print ("Update: environment data has been altered.")
                    print ("Changes found in: " + data[0]["name"] + "... ID: "
                           "" + data[0]["id"])
                    remove_page.start(data[0]["id"])
                    create_page.start(data[0]["id"])
                    changes_made = True
                    continue
            else:
                print ("no changes found.")

            # listed_vms is used in a special case scenario where vm is deleted
            # from an environment. The page will be removed if vm is removed.
            listed_vms = []

            for j in data[0]["vms"]:
                listed_vms.append(j["vm_id"])

            vm_count = 0

            # Check all of the environment's vms.
            for j in cur_data.vms:
                # Has this environment already been rewritten? Skip rest of VMs.
                if changes_made:
                    continue

                # Remove from listed_vms if this vm still exists.
                if str(j.id) in listed_vms:
                    listed_vms.remove(str(j.id))

                vm_count += 1

                # JSON of current VM data is assigned to vm_data.
                print ("\nVM " + str(vm_count) + ": " + j.name + " ... ID: " + str(j.id))
                if os.path.isfile(json_dir + str(j.id) + ".json"):
                    print ("Collecting VM data..."),
                    vm_data = []

                    try:
                        # Make a JSON of VM file info
                        with open(json_dir + str(j.id) + ".json") as f:
                            for line in f:
                                vm_data.append(json.loads(line))

                        # The field where the correct IP can be found varies.
                        tmp_ip_us = ""
                        tmp_ip_india = ""
                        try:
                            # The usual place.
                            for k in j.interfaces[0].nat_addresses.vpn_nat_addresses:
                                if (k.vpn_id == "vpn-3631944" or
                                        k.vpn_id == "vpn-661182"):
                                    tmp_ip_us = k.ip_address
                                elif k.vpn_id == "vpn-3288770":
                                    tmp_ip_india = k.ip_address
                        except (KeyError, IndexError):
                            # Otherwise, get it here.
                            tmp_ip_us = j.interfaces[0].ip

                        # NOTE: these statements will decide if the VM is
                        # up-to-date, or if it is old.
                        print ("checking for changes..."),
                        if (vm_data[0]["id"] != str(j.id) or
                                vm_data[0]["nat_ip_us"] != tmp_ip_us or
                                vm_data[0]["nat_ip_india"] != tmp_ip_india or
                                vm_data[0]["vm_name"] != j.name or
                                vm_data[0]["config_url"] != j.configuration_url or
                                vm_data[0]["vm_hostname"] != j.interfaces[0].hostname):
                                print ("" + vm_data[0]["id"] + " - " + str(j.id))
                                print ("" + vm_data[0]["nat_ip_us"] + " - " + tmp_ip_us)
                                print ("" + vm_data[0]["nat_ip_india"] + " - " + tmp_ip_india)
                                print ("" + vm_data[0]["vm_name"] + " - " + j.name)
                                print ("" + vm_data[0]["config_url"] + " - " + j.configuration_url)
                                print ("" + vm_data[0]["vm_hostname"] + " - " + j.interfaces[0].hostname)
                                # Vm data has been changed; update.
                                print ("changes found.")
                                print ("Update: VM data has been altered.")
                                print ("Changes found in: " + data[0]["name"] + ""
                                       "... ID: " + data[0]["id"] + "... VM: "
                                       "" + vm_data[0]["vm_name"] + "... ID: "
                                       "" + vm_data[0]["id"] + "\n\n")
                                remove_page.start(data[0]["id"])
                                create_page.start(data[0]["id"])
                                changes_made = True
                        else:
                            print ("no changes found.")
                    # NOTE: update this exception handler if running Python 3 to
                    # FileNotFoundError.
                    except IOError:
                        # Another vm has been added to the environment; update.
                        print ("no data found.")
                        print ("Update: VM has been added to environment.")
                        print ("Changes found in: " + data[0]["name"] + "... ID: "
                               "" + data[0]["id"])
                        remove_page.start(data[0]["id"])
                        create_page.start(data[0]["id"])
                        changes_made = True

            print ("\nChecking for recently deleted VMs..."),
            # If there are still elements in listed_vm...
            if len(listed_vms) != 0 and changes_made is False:
                # One or more vms have been removed from environment; update.
                print ("orphaned vm data found. We\'ll code-name it \"Bruce Wayne\".")
                print ("Update: environment has been shot dead in front of Bruce Wayne.")
                print ("Changes found in: " + data[0]["name"] + "... ID: "
                       "" + data[0]["id"] + " ... Cave: of the Bat variety.")
                remove_page.start(data[0]["id"])
                create_page.start(data[0]["id"])
                changes_made = True
            else:
                print ("no orphaned VMs found.")
        else:
            print ("There\'s an environment missing here. Run \"python update"
                   ".py write\" to write it.")

