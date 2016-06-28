"""Update India environments page with current information."""

import json
import pyconfluence as pyco
import skytap
from jinja2 import Template


def start(envs, config_data):
    """Starting point for update_india.py."""

    space = config_data["space"]
    space_parent_id = config_data["space_parent_id"]
    india_name = config_data["india_name"]

    apac = []
    usw = []

    # Append environments related to India/USW VPNs to appropriate lists
    for e in envs:
        for v in e.vms:
            for i in v.interfaces:
                data = json.loads(i.json())
                if ("nat_addresses" in data and
                        "vpn_nat_addresses" in data["nat_addresses"]):
                    for a in data["nat_addresses"]["vpn_nat_addresses"]:
                        if (a["vpn_id"] == "vpn-3288770" and
                                e.name not in apac):
                            apac.append(e.name)
                            print ("APAC - ID: " + str(e.id) + "...Name: "
                                   "" + e.name)
                        elif (a["vpn_id"] == "vpn-3631944" and
                                e.name not in usw):
                            usw.append(e.name)
                            print ("USW - ID: " + str(e.id) + "...Name: "
                                   "" + e.name)

    content = ""

    # Get readyyyyyy to Jinjaaaaa
    with open("update_scripts/update_india/header.html", "r") as f:
        header = Template(f.read())

    with open("update_scripts/update_india/environment.html", "r") as f:
        env = Template(f.read())

    # For both USW and APAC, check if the lists have stuff in them, and then
    # write XHTML for each if so.
    if len(apac) > 0:
        comment = "All APAC environments that have a VPN connection to India are listed below:"
        content += header.render(comment=comment)
        for i in apac:
            content += env.render(name=i)

    if len(usw) > 0:
        content += "<p>&nbsp;</p>"
        comment = "All USW environments that have a VPN connection to India are listed below:"
        content += header.render(comment=comment)
        for i in usw:
            content += env.render(name=i)

    if content != pyco.get_page_content(pyco.get_page_id(india_name, space)):
        pyco.delete_page(pyco.get_page_id(india_name, space))
        pyco.create_page(india_name, space_parent_id, space, content)
    else:
        print ("No differences detected. Page not updated.")
