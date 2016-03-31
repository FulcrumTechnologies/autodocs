"""Update India environments page with current information."""

import confy_actions as confy
import json
import skytap


def start(envs, config_data):
    """Starting point for update_india.py."""

    space = config_data["space"]
    space_parent_id = config_data["space_parent_id"]
    india_name = config_data["india_name"]

    apac = []
    usw = []

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

    if len(apac) > 0:
        content += "<p>All APAC environments that have a VPN connection to India are listed below:</p>"
        for i in apac:
            content += "<p>"
            content += "<ac:link><ri:page ri:content-title=\"" + i + "\" /><ac:plain-text-link-body><![CDATA[" + i + "]]></ac:plain-text-link-body></ac:link>"
            content += "</p>"

    if len(usw) > 0:
        content += "<p>&nbsp;</p><p>All USW environments that have a VPN connection to India are listed below:</p>"
        for i in apac:
            content += "<p>"
            content += "<ac:link><ri:page ri:content-title=\"" + i + "\" /><ac:plain-text-link-body><![CDATA[" + i + "]]></ac:plain-text-link-body></ac:link>"
            content += "</p>"

    if content != confy.get_page_content(confy.get_page_id(india_name, space)):
        confy.delete_page(confy.get_page_id(india_name, space))
        confy.create_page(india_name, space_parent_id, space, content)
    else:
        print ("No differences detected. Page not updated.")

