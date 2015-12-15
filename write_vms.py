#!/usr/bin/env python

# -----------------------------------------------------------------------------
# write_vms.py
#
# Creates content in xhtml that will be posted to new page. Also creates json
# that will be used to hold information, stored in /JSONS directory. Lastly,
# write_page.py is called to request the Confluence API and write the page.
# -----------------------------------------------------------------------------


def create_one(i, parent_id, parent_name):
    """Just make one vm page; primarily called by create(), seen below."""
    import json
    import write_page

    # Making a json containing important information. This will be stored in
    # a file in JSONS directory and used to perform various functions
    # related to Wiki Keeper.
    json_info = {}

    vm_name = i["interfaces"][0]["hostname"]
    vm_id = i["id"]

    json_info["vm_name"] = vm_name

    json_info["parent_page_id"] = parent_id

    json_info["parent_page_name"] = parent_name

    content = "<p>"

    content += ("ID: " + vm_id + "<br/><br/>")
    json_info["id"] = vm_id

    content += ("Configuration URL: " + i["configuration_url"] + "<br/><br/>")
    json_info["config_url"] = i["configuration_url"]

    content += ("NAT IP: " + i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"] + "<br/>")
    json_info["nat_ip"] = i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"]

    content += ("VPN ID: " + i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["vpn_id"] + "<br/><br/>")
    json_info["vpn_id"] = i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["vpn_id"]

    try:
        content += ("External IP: " + i["interfaces"][0]["services"][0]["external_ip"] + "<br/>")
        json_info["external_ip"] = i["interfaces"][0]["services"][0]["external_ip"]
    except IndexError:
        pass

    try:
        content += ("External port: " + str(i["interfaces"][0]["services"][0]["external_port"]) + "<br/>")
        json_info["external_port"] = str(i["interfaces"][0]["services"][0]["external_port"])
    except IndexError:
        pass

    try:
        content += ("Internal port: " + str(i["interfaces"][0]["services"][0]["internal_port"]) + "<br/><br/>")
        json_info["internal_port"] = str(i["interfaces"][0]["services"][0]["internal_port"])
    except IndexError:
        pass

    content += ("Local IP: " + i["interfaces"][0]["ip"] + "<br/>")
    json_info["local_ip"] = i["interfaces"][0]["ip"]

    content += ("<br/>------------------------<br/>Note: Wiki Keeper is a WIP; ")
    content += ("other super fun and magical features are under development.</p>")

    feedback, json_info = write_page.create("" + vm_name + " - [" + parent_name + "]",
                                            str(parent_id), content, json_info)

    with open("JSONS/" + vm_id + ".json", "w") as file:
        json.dump(json_info, file)


def create(data, parent_id, parent_name):
    """Create vm wiki page(s)."""
    import json
    import write_page

    # -------------------------------------------------------------------------

    for i in data["vms"]:
        create_one(i, parent_id, parent_name)

