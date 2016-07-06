"""Write wiki pages of environments which currently have none."""

import build_page
import commands
import copy
import json
import pyconfluence as pyco
import skytap
import skytapdns
import re


def clean_content(content):
    """Clean content of 'random' values for matching purposes."""
    while "ac:macro-id=" in content:
        # We want to remove these bits since the string following is randomly
        # determined, making it difficult to determine if there is new info
        # TODO: stop being lazy and try regex here
        content = content[0:content.find("ac:macro-id=")-1] + content[content.find("ac:macro-id=")+64:]

    return content


def start(envs, config_data):
    """Write all remaining pages of environments not currently listed."""

    # Make sure you've configured config.yml! Else, this will crash the process.
    space = config_data["space"]
    parent_id = config_data["parent_id"]
    other_docs_id = config_data["other_docs_id"]

    # Just counting up the total number, for stats
    env_all = 0
    env_written = 0
    env_failed = 0

    # Get second set of Skytap environment objects.
    # Temporary solution to the "for loop destroying envs list" problem
    copy_envs_dns = skytap.Environments()
    copy_envs_vms = skytap.Environments()

    for e in envs:
        if "burke" not in e.name.lower():
            continue

        # Excluding environment(s)
        if "CATS Interim Solution QA Environment" in e.name:
            continue

        print ("\n--------------------\nTrying " + e.name + " ("
               "" + str(e.id) + ")...")
        env_all += 1

        # Get copies of environment object from copy_envs to deal with dns stuff
        # and vms stuff
        e_copy_dns = copy_envs_dns[e.id]
        e_copy_vms = copy_envs_vms[e.id]

        # Use build_page.py to construct XHTML source based on info about e
        print ("Fetching current environment information...")
        content = build_page.build_env(e)

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
            env_page_id = json.loads(pyco.get_page_full_more(e.name, space))["results"][0]["id"]
            cleaned_content_1 = clean_content(content)
            cleaned_content_2 = clean_content(pyco.get_page_content(env_page_id))

            # Compare content, sans randomness
            if cleaned_content_1 == cleaned_content_2:
                print ("Page for " + str(e.id) + " exists but there is nothing "
                       "to change.\nSkipping...")
                continue
            else:
                print ("Page for " + str(e.id) + " exists and has outdated "
                       "information.\nDeleting in preparation for rewrite...")
                pyco.delete_page_full(env_page_id)
        except IndexError:
            print ("No page found for " + str(e.id) + ".")
            pass

        print ("Writing content to Confluence for " + str(e.id) + "...")
        try:
            # Only mess with DNS stuff if environment page is changed.
            skytapdns.recreate_all_vm_dns(e_copy_dns, True)
            # Create page
            result = json.loads(pyco.create_page(e.name,
                                parent_id, space, content))
        except TypeError:
            # Can't parse this because of "oops!" message, just continue to next
            # Reasons for this: parent_id not valid, name not valid ("+", "/")
            print ("Write failed.")
            env_failed += 1
            continue

        # Implied from the fact that we didn't hit the TypeError above.
        print ("Write successful!")

        print ("Writing VMs for " + e.name + "...")
        try:
            # Getting ID of newly-written Confluence page to write under
            parent_page_id = result["id"]

            for v in e_copy_vms.vms:
                print ("==========\nTrying " + str(v.id) + "...")

                print ("Fetching current VM information...")
                # Build page
                hostname, content = build_page.build_vm(v)

                new_page_name = (hostname + " - " + v.name + " - "
                                 "" + e_copy_vms.name)

                print ("Checking if " + str(v.id) + " currently has existing "
                       "page...")
                try:
                    vm_page_id = json.loads(pyco.get_page_full_more(new_page_name, space))["results"][0]["id"]
                    print ("Page for " + str(v.id) + " exists.\nDeleting in "
                           "preparation for rewrite (this is normal)...")
                    pyco.delete_page(vm_page_id)
                except IndexError:
                    print ("No page found for " + str(v.id) + ".")
                    pass

                print ("Writing content to Confluence for " + str(v.id) + "...")
                pyco.create_page(hostname + " - " + v.name + " - " + e_copy_vms.name, parent_page_id, space, content)
                print ("Write successful!")

            env_written += 1
        except (TypeError, KeyError):
            print ("Oops, I lied. Write was apparently successful, but the "
                   "page ID could not be obtained.\nVM pages cannot be written."
                   "\nMoving to next.")
            env_failed += 1
            continue

    print ("\n\n\n--------------------")
    print ("Total environments: " + str(env_all))
    print ("Total environments written: " + str(env_written))
    print ("Total environments failed: " + str(env_failed))
