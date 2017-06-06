"""Write wiki pages of environments which currently have none."""

import build_page
import commands
import copy
import json
import pyconfluence as pyco
import skytap
import skytapdns
import re
import time


def clean_name(name):
    """Clean name of environment."""
    return name.replace("+", "(and)").replace("/", "(slash)").strip()


def clean_content(content):
    """Clean content of 'random' values for matching purposes."""
    while "ac:macro-id=" in content:
        # We want to remove these bits since the string following is randomly
        # determined, making it difficult to determine if there is new info
        # TODO: stop being lazy and try regex here
        content = content[0:content.find("ac:macro-id=")-1] + content[content.find("ac:macro-id=")+64:]

    content = content.replace("<p></p>", "<p />")

    return content


def start(envs, config_data, name_filter=None):
    """Write Confluence pages for Skytap environments."""

    cur_hour = int(time.strftime("%H"))
    print ("Current hour: " + str(cur_hour))

    # Make sure you've configured config.yml! Else, this will crash the process.
    space = config_data["space"]
    parent_id = config_data["parent_id"]
    other_docs_id = config_data["other_docs_id"]

    # Just counting up the total number, for stats and numbers and things
    env_all = 0
    env_written = 0
    env_failed = 0

    # Get second set of Skytap environment objects.
    # Temporary solution to the "for loop destroying envs list" problem
    copy_envs_dns = skytap.Environments()

    for e in envs:
        # If user gave a name filter in parameters, then check for that in name
        if name_filter and name_filter not in e.name:
                continue

        print ("\n--------------------\nTrying " + clean_name(e.name) + " ("
               "" + str(e.id) + ")...")
        env_all += 1

        # Get copies of environment object from copy_envs to deal with dns stuff
        # and vms stuff
        e_copy_dns = copy_envs_dns[e.id]

        # Use build_page.py to construct XHTML source based on info about e
        print ("Fetching current environment information...")
        try:
            content = build_page.build_env(e)
        except TypeError as err:
            print ("ERROR: TypeError encountered during page build - ", err)
            continue

        # If a page with the same name is found:
        # - If content is the same, then there is nothing to change. Continue.
        # - If content differs, delete the current page and create new one with
        #   content.
        # Otherwise, page does not exist, and continue to write new page.
        print ("Checking if " + str(e.id) + " currently has existing page...")
        try:
            # Due to macro stuff, random strings are generated and those will
            # make the environment rewrite itself every time. So let's compare
            # "clean" versions of the environments, with randomness removed.
            env_page_id = json.loads(pyco.get_page_full_more(clean_name(e.name), space))["results"][0]["id"]
            cleaned_content_1 = clean_content(content)
            cleaned_content_2 = clean_content(pyco.get_page_content(env_page_id))

            # Compare content, sans randomness
            if cur_hour > 2 and cleaned_content_1 == cleaned_content_2:
                print ("Page for " + str(e.id) + " exists but there is nothing "
                       "to change.\nSkipping...")
                continue
            else:
                print ("Page for " + str(e.id) + " exists and has outdated "
                       "information.\nPreparing to rewrite...")
        except IndexError:
            # No page found, so we want to write one. Continue on!
            print ("No page found for " + str(e.id) + ".")
            pass

        try:
            # Only mess with DNS stuff if environment page is changed.
            try:
                skytapdns.recreate_all_vm_dns(e_copy_dns, True)
            except ValueError:
                print ("ERROR: JSON VALUES COULDN'T BE FOUND, GO BOTHER THE "
                       "INTERN ABOUT THIS FOR BEST RESULTS")
            # Create page
            print ("Writing content to Confluence for " + str(e.id) + "...")
            try:
                result = json.loads(pyco.edit_page(pyco.get_page_id(clean_name(e.name), space),
                                    clean_name(e.name), space, content))
                print ("Edit successfull!")
            except ValueError:
                result = json.loads(pyco.create_page(clean_name(e.name),
                                    parent_id, space, content))
                print ("Write successfull!")
        except TypeError:
            # Can't parse this because of "oops!" message, just continue to next
            # Reasons for this: parent_id not valid, name not valid ("+", "/")
            print ("Write failed.")
            env_failed += 1

    print ("\n\n\n--------------------")
    print ("Total environments: " + str(env_all))
    print ("Total environments written: " + str(env_written))
    print ("Total environments failed: " + str(env_failed))
