#!/usr/bin/env python

"""write_env.py

Creates content in xhtml that will be posted to new page. Also creates json
that will be used to hold information, stored in /JSONS directory. Lastly,
write_page.py is called to request the Confluence API and write the page.
"""

import httplib
import json
import os
import urllib2
import urlparse
import write_page


def check_url(url):
    """Check if given URL directs to existing page. Return true if so."""
    # Return true for now, until a better method can be concocted.
    # Current method works but takes up to 60 seconds before timing out and
    # returning False.
    return True

    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


def clean_string(str):
    """Clean up lone apostrophes and quotations in string."""
    str = str.replace("\'", "")

    return str


def create(data, parent_id):
    """Create environment wiki page."""

    print ("Writing content..."),

    # Making a json containing important information. This will be stored in a
    # file in JSONS directory and used to perform various functions related to
    # Wiki Keeper.
    json_info = {}

    # Placeholder variables.
    undef = "Unavailable"
    undef_err = "Unavailable: data missing"

    env_id = data["id"]
    env_name = clean_string(data["name"])

    config_url = data["url"]
    puppet_enabled = undef
    admin_access = undef
    user_access = undef

    json_info["name"] = env_name
    json_info["id"] = env_id
    json_info["config_url"] = config_url
    json_info["puppet_enabled"] = puppet_enabled
    json_info["admin_access"] = admin_access
    json_info["user_access"] = user_access

    json_info["vms"] = []
    json_info["db"] = []

    new_db = {}
    db_exists = False
    db_id = undef

    # Initially these are hardcoded. Change later.
    port_home = 8443
    port_reports = 8444
    port_services = 8445
    port_mob = 8446

    storage_dir = "storage/"

    if os.path.isfile(storage_dir + env_id + ".json"):
        stored = []

        # Make a JSON out of file info
        with open(storage_dir + env_id + ".json") as f:
            for line in f:
                stored.append(json.loads(line))

        comment = stored[0]["comment"]
        user = stored[0]["user"]
        password = stored[0]["password"]
    else:
        comment = ("This page is being monitored and updated automatically by "
                   "tech wizardry. Consult your local tech wizards or their IT "
                   "intern/minion if there is information you would like to "
                   "edit.")
        user = "?"
        password = "?"

    # Initial block.
    content = ("<ac:layout><ac:layout-section ac:type=\\\"two_equal\\\"><ac:lay"
               "out-cell><p>" + comment + "</p></ac:layout-cell><ac:layout"
               "-cell><p>&nbsp;</p></ac:layout-cell></ac:layout-section>")

    content += ("<ac:layout-section ac:type=\\\"two_equal\\\">")
    content += ("<ac:layout-cell>")

    vm_content = ""
    lb_content = ""

    for i in data["vms"]:
        vm_name = i["name"]
        vm_hostname = i["interfaces"][0]["hostname"]
        vm_id = i["id"]
        vm_user = undef
        vm_pass = undef
        ssh_enabled = undef
        ssl_enabled = undef

        try:
            vm_ip = i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"]
        except (KeyError, IndexError):
            vm_ip = i["interfaces"][0]["ip"]

        base_url = "https://" + vm_ip

        services = []

        for i in i["interfaces"][0]["services"]:
            new_service = {}
            new_service["internal_ip"] = vm_ip
            new_service["internal_port"] = str(i["internal_port"])
            new_service["external_ip"] = i["external_ip"]
            new_service["external_port"] = str(i["external_port"])
            services.append(new_service)

        new_vm = {}
        new_vm["vm_name"] = vm_name
        new_vm["vm_hostname"] = vm_hostname
        new_vm["vm_ip"] = vm_ip
        new_vm["vm_id"] = vm_id
        new_vm["vm_base_url"] = base_url
        new_vm["vm_user"] = vm_user
        new_vm["vm_pass"] = vm_pass
        new_vm["vm_ssh_enabled"] = ssh_enabled
        new_vm["vm_ssl_enabled"] = ssl_enabled
        new_vm["services"] = services

        # This will hold content for each vm "block"
        vm_info = []

        if vm_hostname != "lb":
            vm_content += ("<h2><strong style=\\\"line-height: 1.4285715;\\\">" + vm_name + "</strong></h2>")
            vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">VM ID: " + vm_id + "</p>")
            vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">IP: " + vm_ip + "</p>")

            serv_count = 0
            for j in services:
                serv_count += 1
                vm_content += ("<p><strong> - Service " + str(serv_count) + ":</strong></p>")
                vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">Internal Port: " + j["internal_port"] + "</p>")
                vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">External IP: <a href=\\\"" + j["external_ip"] + "\\\">" + j["external_ip"] + "</a></p>")
                vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">External Port: " + j["external_port"] + "<span style=\\\"line-height: 1.4285715;\\\">&nbsp;</span></p>")
        else:
            lb_content += ("<h2><strong style=\\\"line-height: 1.4285715;\\\">" + vm_name + "</strong></h2>")
            lb_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Web: (URL/home/reports/services/mobility): </p>")
            lb_content += ("<p style=\\\"margin-left: 30.0px;\\\"> - <a href=\\\"" + base_url + "/cats/\\\">" + base_url + "/cats/</a></p>")
            lb_content += ("<p style=\\\"margin-left: 30.0px;\\\"> - <a href=\\\"" + base_url + "/cats/\\\">" + base_url + ":" + str(port_home) + "/cats/</a></p>")
            lb_content += ("<p style=\\\"margin-left: 30.0px;\\\"> - <a href=\\\"" + base_url + "/cats/\\\">" + base_url + ":" + str(port_reports) + "/cats/</a></p>")
            lb_content += ("<p style=\\\"margin-left: 30.0px;\\\"> - <a href=\\\"" + base_url + "/cats/\\\">" + base_url + ":" + str(port_services) + "/cats/</a></p>")
            lb_content += ("<p style=\\\"margin-left: 30.0px;\\\"> - <a href=\\\"" + base_url + "/cats/\\\">" + base_url + ":" + str(port_mob) + "/cats/</a></p>")

        if vm_hostname == "db":
            # This data will be used shortly, for creating the database table.
            db_exists = True
            db_id = vm_id
            db_ip = vm_ip
            db_user = vm_user
            db_pass = vm_pass
            db_ssh = ssh_enabled
            db_ssl = ssl_enabled
            db_port = 1521
            db_sid = "orcl"

            # If there is a db vm, this information will be added to db dict.
            new_db["db_id"] = db_id
            new_db["db_ip"] = db_ip
            new_db["db_user"] = db_user
            new_db["db_pass"] = db_pass
            new_db["db_ssh"] = db_ssh
            new_db["db_ssl"] = db_ssl
            new_db["db_port"] = str(db_port)
            new_db["db_sid"] = db_sid

        json_info["vms"].append(new_vm)

    json_info["db_id"] = db_id

    # db_exists will always be in db dict even if there is no db vm. For this
    # reason, it is added after everything else is done.
    new_db["db_exists"] = str(db_exists)
    json_info["db"].append(new_db)

    content += ("" + lb_content + vm_content)

    content += ("</ac:layout-cell>")
    content += ("<ac:layout-cell>")
    content += ("<p><strong>Additional Details</strong></p>")
    content += ("<p>Config ID: " + str(env_id) + "</p>")
    content += ("<p>Admin User: " + user + "</p>")
    content += ("<p>Admin PW: " + password + "</p>")
    content += ("<p>Skytap environment link:&nbsp;<a href=\\\"" + config_url + "\\\">" + config_url + "</a></p>")
    content += ("<p>&nbsp;</p>")

    if db_exists:
        content += ("<p><strong>Oracle DB Info</strong></p>")
        content += ("<ul><li>Oracle OS User: &nbsp;oracle</li>")
        content += ("<li>Host: " + db_ip + "</li>")
        content += ("<li>DB Schema:&nbsp;CATS</li>")
        content += ("<li>DB Password:&nbsp;CATS</li>")
        content += ("<li>SID:&nbsp;" + db_sid + "</li>")
        content += ("<li>Port: " + str(db_port) + "</li>")
        content += ("</ul>")

    content += ("<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>")

    qr_url = ("<img src=\\\"http://api.qrserver.com/v1/create-qr-code/?data=lb."
              "" + str(env_id) + ".skytap.fulcrum.net:" + str(port_mob) + ":1::"
              "" + env_name + "&amp;size=150x150\\\" />")

    # The qr_url in json_info will have "extra" escape chars (backslashes), but
    # it is included in json_info just in case.
    json_info["qr_url"] = qr_url

    content += ("<table><tbody><tr><th><p>QR Code for Configuration:</p><p>"
                "(Android only)</p></th><th>" + qr_url + "</th></tr></tbody>"
                "</table><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>")

    content += ("</ac:layout-cell></ac:layout-section></ac:layout>")

    content = clean_string(content)

    # -------------------------------------------------------------------------

    feedback, json_info = write_page.create(env_name, str(parent_id), content, json_info)

    if feedback != 0:
        with open("JSONS/" + env_id + ".json", "w") as file:
            json.dump(json_info, file)

    return feedback, env_name

