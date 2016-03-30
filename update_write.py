"""Write wiki pages of environments which currently have none."""

import build_page
import confy_actions as confy
import copy
import json
import skytap


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

    existing_envs = []

    for e in envs:
        existing_envs.append(e.name + " -- AutoDocs")

        print ("\n--------------------\nTrying " + e.name + " ("
               "" + str(e.id) + ")...")
        env_all += 1

        print ("Fetching current environment information...")
        content = build_page.build_env(e)

        # If a page with the same name is found:
        # - If content is the same, then there is nothing to change. Continue.
        # - If content differs, delete the current page and create new one with
        #   content.
        # Otherwise, page does not exist, and continue to write new page.
        print ("Checking if " + str(e.id) + " currently has existing page...")
        try:
            env_page_id = json.loads(confy.get_page_full_more(e.name + " -- AutoDocs", space))["results"][0]["id"]
            if content == confy.get_page_content(env_page_id):
                print ("Page for " + str(e.id) + " exists but there is nothing "
                       "to change.\nSkipping...")
                continue
            else:
                if e.name.startswith("VZW"):
                    print ("Page for " + str(e.id) + " will not be updated "
                           "since it is a VZW environment.")
                    continue
                print ("Page for " + str(e.id) + " exists and has outdated "
                       "information.\nDeleting in preparation for rewrite...")
                confy.delete_page_full(env_page_id)
        except IndexError:
            print ("No page found for " + str(e.id) + ".")
            pass

        print ("Writing content to Confluence for " + str(e.id) + "...")
        try:
            result = json.loads(confy.create_page(e.name + " -- AutoDocs",
                                parent_id, space, content))
        except TypeError:
            # Can't parse this because of "oops!" message, just continue to next
            print ("Write failed.")
            env_failed += 1
            continue

        print ("Write successful!")

        if e.name.startswith("VZW"):
            print ("This is a Verizon environment; as such, no VM pages will be"
                   " generated.")
            continue

        new_envs = skytap.Environments()
        new_e = new_envs[e.id]

        print ("Writing VMs for " + e.name + "...")
        try:
            parent_page_id = result["id"]

            for v in new_e.vms:
                print ("==========\nTrying " + str(v.id) + "...")

                print ("Fetching current VM information...")
                hostname, content = build_page.build_vm(v)

                new_page_name = (hostname + " - " + v.name + " - "
                                 "" + new_e.name + " -- AutoDocs")

                print ("Checking if " + str(v.id) + " currently has existing "
                       "page...")
                try:
                    vm_page_id = json.loads(confy.get_page_full_more(new_page_name, space))["results"][0]["id"]
                    print ("Page for " + str(v.id) + " exists.\nDeleting in "
                           "preparation for rewrite (this is normal)...")
                    confy.delete_page(vm_page_id)
                except IndexError:
                    print ("No page found for " + str(v.id) + ".")
                    pass

                print ("Writing content to Confluence for " + str(v.id) + "...")
                confy.create_page(hostname + " - " + v.name + " - " + new_e.name + " -- AutoDocs", parent_page_id, space, content)
                print ("Write successful!")

            env_written += 1
        except (TypeError, KeyError):
            print ("Oops, I lied. Write was apparently successful, but the "
                   "page ID could not be obtained.\nVM pages cannot be written."
                   "\nMoving to next.")
            env_failed += 1
            continue

    #written_envs = json.loads(confy.get_page_children(parent_id))

    #print ("++++++++++++++++++++")
    #print ("Checking for environment pages that no longer should exist...")
    #for i in written_envs["results"]:
    #    if (i["title"] + " -- AutoDocs") not in existing_envs:
    #        print ("Deleting " + e.name + " -- AutoDocs...")
    #        confy.delete_page_full(confy.get_page_id(i["title"] + " -- AutoDocs", space))
    #        print ("Done!")

    envs = skytap.Environments()

    content = "Any and all VZW environments with published services will be listed below.<br/>"

    for e in envs:
        env_found = False
        if e.name.startswith("VZW"):
            for v in e.vms:
                for i in v.interfaces:
                    for s in i.services:
                        content += "<p>"
                        content += "<ac:link><ri:page ri:content-title=\\\"" + e.name + " -- AutoDocs\\\" /><ac:plain-text-link-body><![CDATA[" + e.name + " --AutoDocs (" + str(e.id) + ")]]></ac:plain-text-link-body></ac:link>"
                        content += "</p>"
                        env_found = True
                        break
                    if env_found:
                        break
                if env_found:
                    break

    print content

    confy.delete_page(confy.get_page_id("VZW Published Services", space))
    confy.create_page("VZW Published Services", other_docs_id, space, content)

    print ("\n\n\n--------------------")
    print ("Total environments: " + str(env_all))
    print ("Total environments written: " + str(env_written))
    print ("Total environments failed: " + str(env_failed))

