#!/usr/bin/env python

"""write_vms.py

Creates content in xhtml that will be posted to new page. Also creates json
that will be used to hold information, stored in /JSONS directory. Lastly,
write_page.py is called to request the Confluence API and write the page.
"""

import json
import write_page


def create_one(i, parent_id, parent_name):
    """Just make one vm page; primarily called by create(), seen below."""

    print (i["name"] + ": Writing content..."),

    # Making a json containing important information. This will be stored in
    # a file in JSONS directory and used to perform various functions
    # related to Wiki Keeper.
    json_info = {}

    vm_name = i["name"]
    vm_hostname = i["interfaces"][0]["hostname"]
    vm_id = i["id"]

    json_info["vm_name"] = vm_name
    json_info["vm_hostname"] = vm_hostname
    json_info["parent_page_id"] = parent_id
    json_info["parent_page_name"] = parent_name

    content = "<p>"

    content += ("ID: " + vm_id + "<br/><br/>")
    json_info["id"] = vm_id

    content += ("Configuration URL: " + i["configuration_url"] + "<br/>")
    json_info["config_url"] = i["configuration_url"]

    json_info["nat_ip_us"] = ""
    json_info["nat_ip_india"] = ""

    try:
        content += ("<br/>")
        for k in i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"]:
            if k["vpn_name"].startswith("US"):
                content += ("NAT IP (US): " + k["ip_address"] + "<br/>")
                json_info["nat_ip_us"] = k["ip_address"]
            elif k["vpn_name"].startswith("SG"):
                content += ("NAT IP (India): " + k["ip_address"] + "<br/>")
                json_info["nat_ip_india"] = k["ip_address"]
    except (KeyError, IndexError):
        content += ("NAT IP (US): " + i["interfaces"][0]["ip"] + "<br/>")
        json_info["nat_ip_us"] = i["interfaces"][0]["ip"]
        json_info["nat_ip_india"] = ""

    json_info["vpn_id_us"] = ""
    json_info["vpn_id_india"] = ""

    try:
        for k in i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"]:
            if k["vpn_name"].startswith("US"):
                content += ("VPN ID (US): " + k["vpn_id"] + "<br/>")
                json_info["vpn_id_us"] = k["vpn_id"]
            elif k["vpn_name"].startswith("SG"):
                content += ("VPN ID (India): " + k["vpn_id"] + "<br/>")
                json_info["vpn_id_india"] = k["vpn_id"]
    except (KeyError, IndexError):
        # Can't find "nat_addresses"
        pass

        content += ("<br/>")

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

    content += ("</p>")

    feedback, json_info = write_page.create("" + vm_hostname + " - " + vm_name + " - [" + parent_name + "]",
                                            str(parent_id), content, json_info)

    if feedback != 0:
        with open("JSONS/" + vm_id + ".json", "w") as file:
            json.dump(json_info, file)


def create(data, parent_id, parent_name):
    """Create vm wiki page(s)."""

    print ("Writing pages for vms.")

    for i in data["vms"]:
        create_one(i, parent_id, parent_name)

