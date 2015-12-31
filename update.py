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


def check(envs):
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

            for j in data[0]["vms"]:
                listed_vms.append(j["vm_id"])

            vm_count = 0
            # Check all of the environment's vms.
            for j in cur_data["vms"]:
                vm_count += 1

                # JSON of current VM data is assigned to vm_data.
                print ("\nVM " + str(vm_count) + ": " + j["name"] + " ... ID: " + j["id"])
                if os.path.isfile(json_dir + j["id"] + ".json"):
                    print ("Collecting VM data..."),
                    vm_data = []

                    try:
                        # Make a JSON of VM file info
                        with open(json_dir + j["id"] + ".json") as f:
                            for line in f:
                                vm_data.append(json.loads(line))

                        # The field where the correct IP can be found varies.
                        tmp_ip_india = ""
                        try:
                            # The usual place.
                            for k in j["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"]:
                                if k["vpn_name"].startswith("US"):
                                    tmp_ip_us = k["ip_address"]
                                elif k["vpn_name"].startswith("SG"):
                                    tmp_ip_india = k["ip_address"]
                        except (KeyError, IndexError):
                            # Otherwise, get it here.
                            tmp_ip_us = j["interfaces"][0]["ip"]

                        # NOTE: these statements will decide if the VM is
                        # up-to-date, or if it is old.
                        print ("checking for changes..."),
                        if (vm_data[0]["id"] != j["id"] or
                                vm_data[0]["nat_ip_us"] != tmp_ip_us or
                                vm_data[0]["nat_ip_india"] != tmp_ip_india or
                                vm_data[0]["vm_name"] != j["name"] or
                                vm_data[0]["config_url"] != j["configuration_url"] or
                                vm_data[0]["vm_hostname"] != j["interfaces"][0]["hostname"]):
                                # Vm data has been changed; update.
                                print ("changes found.")
                                print ("Update: VM data has been altered.")
                                print ("Changes found in: " + data[0]["name"] + ""
                                       "... ID: " + data[0]["id"] + "... VM: "
                                       "" + vm_data[0]["vm_name"] + "... ID: "
                                       "" + vm_data[0]["id"] + "\n\n")
                                remove_page.start(data[0]["id"])
                                create_page.start(data[0]["id"])
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

                # Remove from listed_vms if this vm still exists.
                if j["id"] in listed_vms:
                    listed_vms.remove(j["id"])

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
        else:
            print ("There\'s an environment missing here. Run \"python update"
                   ".py write\" to write it.")

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
            else:
                print ("no environments have been deleted.")
        except (IndexError, KeyError):
            pass


def store(envs):
    """Store specific data from pages to preserve through future updates."""

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

    location = config_data["wiki_url"]
    username = config_data["wiki_user"]
    password = config_data["wiki_pass"]

    json_dir = "JSONS/"
    storage_dir = "storage/"

    for i in envs:
        # Get JSON matching environment ID
        if os.path.isfile(json_dir + i["id"] + ".json"):
            print ("Storing data of " + i["name"] + " ... ID: " + i["id"])
            print ("Collecting environment data..."),
            data = []

            # Make a JSON out of file info
            with open(json_dir + i["id"] + ".json") as f:
                for line in f:
                    data.append(json.loads(line))

            print ("fetching page source..."),
            curl_cmd = ("curl -s -u " + username + ":" + password + " "
                        "" + location + data[0]["page_id"] + "?expand=body.stor"
                        "age | python -mjson.tool > temp.json")

            output = os.system(curl_cmd)

            with open("temp.json") as file:
                result = json.load(file)

            # Empties temp.json
            open("temp.json", 'w').close()

            storage_info = {}
            content = result["body"]["storage"]["value"]

            # NOTE: this is where the magic happens. Add elements here.
            print ("storing relevant information in JSON..."),
            storage_info["comment"] = content[content.find("<ac:layout-cell><p>")+19:content.find("</p></ac:layout-cell>")]
            storage_info["user"] = content[content.find("Admin User*:")+12:content.find("</p><p>Admin PW*:")].strip()
            storage_info["password"] = content[content.find("Admin PW*:")+10:content.find("</p><p>Skytap environment")].strip()
            storage_info["mob_ver"] = content[content.find("Version*:")+9:content.find("</p><p>APK Build")].strip()
            storage_info["apk_build"] = content[content.find("APK Build*:")+11:content.find("</p><p>WAR Build")].strip()
            storage_info["war_build"] = "?" #content[content.find("WAR Build*:")+11:content.find("</p><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><table>")]

            with open(storage_dir + i["id"] + ".json", "w") as file:
                json.dump(storage_info, file)

            print ("done.\n")


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
        write(envs)
    elif (args[1] == "check"):
        os.system("clear")
        print ("Updating existing wiki pages.")
        check(envs)
    elif (args[1] == "store"):
        os.system("clear")
        print ("Storing updated information from wiki pages.")
        store(envs)
    elif (args[1] == "reset"):
        os.system("clear")
        print ("Resetting all wiki pages.")
        reset(envs)
    else:
        print ("Command not recognized. Use \"write\" or \"check\".")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)

