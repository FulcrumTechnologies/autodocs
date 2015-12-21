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

    # --- Writing content for all of row 1 of the environment page template ---
    # This content includes everything up until the "Server Access" tables.

    with open("content_1.txt", "r") as file:
        to_read = file.read().replace('\n', '')

    env_id = data["id"]
    env_name = data["name"]
    env_name = clean_string(env_name)

    config_url = data["url"]
    puppet_enabled = undef
    admin_access = undef
    user_access = undef

    content = (to_read % (config_url, config_url, undef, undef, undef))

    json_info["name"] = env_name
    json_info["id"] = env_id
    json_info["config_url"] = config_url
    json_info["puppet_enabled"] = puppet_enabled
    json_info["admin_access"] = admin_access
    json_info["user_access"] = user_access

    # --- Writing content for row 2, col 1 of the environment page template ---
    # This content lists the URL for the vm, as well as homes/reports/services.

    content += ("<ac:layout-section ac:type=\\\"two_equal\\\"><ac:layout-cell><h3><strong>Server Access:</strong></h3>")
    json_info["vms"] = []
    json_info["db"] = []

    new_db = {}
    db_exists = False

    # Initially these are hardcoded. Change later.
    port_home = 8443
    port_reports = 8444
    port_services = 8445
    port_api = 8446

    for i in data["vms"]:
        vm_name = i["interfaces"][0]["hostname"]
        vm_id = i["id"]
        vm_user = undef
        vm_pass = undef
        ssh_enabled = undef
        ssl_enabled = undef

        try:
            vm_ip = i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"]
            base_url = "https://" + i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"]
        except (KeyError, IndexError):
            vm_ip = undef_err
            base_url = undef_err

        try:
            internal_port = str(i["interfaces"][0]["services"][0]["internal_port"])
        except IndexError:
            internal_port = undef_err

        try:
            external_port = str(i["interfaces"][0]["services"][0]["external_port"])
        except IndexError:
            external_port = undef_err

        new_vm = {}
        new_vm["vm_name"] = vm_name
        new_vm["vm_ip"] = vm_ip
        new_vm["vm_id"] = vm_id
        new_vm["vm_base_url"] = base_url
        new_vm["vm_user"] = vm_user
        new_vm["vm_pass"] = vm_pass
        new_vm["vm_ssh_enabled"] = ssh_enabled
        new_vm["vm_ssl_enabled"] = ssl_enabled
        new_vm["vm_internal_port"] = internal_port
        new_vm["vm_external_port"] = external_port

        # "db" is the database, and gets its own table later on. Skip for now.
        if vm_name != "db":
            content += ("<table><tbody>")
            content += ("<tr><th>" + vm_name + "</th><th>&nbsp;</th></tr>")
            content += ("<tr><td>ID:</td><td>" + vm_id + "</td></tr>")
            content += ("<tr><td>Host IP Address:</td><td>" + vm_ip + "</td></tr>")
            content += ("<tr><td><p>User:</p></td><td>" + vm_user + "</td></tr>")
            content += ("<tr><td>Password:</td><td>" + vm_pass + "</td></tr>")

            if internal_port != undef_err:
                content += ("<tr><td>Internal Port:</td><td>" + internal_port + "</td></tr>")
            if external_port != undef_err:
                content += ("<tr><td>External Port:</td><td>" + external_port + "</td></tr>")

            content += ("<tr><td>SSH:</td><td><ac:task-list><ac:task><ac:task-id>"
                        "9</ac:task-id><ac:task-status>" + ssh_enabled + "</ac:task-status>"
                        "<ac:task-body><span>&nbsp;</span></ac:task-body></ac:task>"
                        "</ac:task-list></td></tr>")
            content += ("<tr><td>SSL:</td><td><ac:task-list><ac:task><ac:task-id>"
                        "10</ac:task-id><ac:task-status>" + ssl_enabled + "</ac:task-status>"
                        "<ac:task-body><span>&nbsp;</span></ac:task-body></ac:task>"
                        "</ac:task-list></td></tr>")
            content += ("</tbody></table>")
        else:
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

    # db_exists will always be in db dict even if there is no db vm. For this
    # reason, it is added after everything else is done.
    new_db["db_exists"] = str(db_exists)
    json_info["db"].append(new_db)

    # End of row 2, column 1.
    content += ("<p><strong><br /></strong></p></ac:layout-cell>")

    # ---------------- Writing content for database (db) table ----------------

    content += ("<ac:layout-cell><table><tbody><tr><th>Database (db)</th>")

    if db_exists:
        content += ("<th>&nbsp;</th></tr>")
        content += ("<tr><td>Host IP Address:</td><td>" + db_ip + "</td></tr>")
        content += ("<tr><td>User:</td><td>" + db_user + "</td></tr>")
        content += ("<tr><td>Password:</td><td>" + db_pass + "</td></tr>")
        content += ("<tr><td>SSH:</td><td><ac:task-list><ac:task><ac:task-id>"
                    "9</ac:task-id><ac:task-status>" + db_ssh + "</ac:task-status>"
                    "<ac:task-body><span>&nbsp;</span></ac:task-body></ac:task>"
                    "</ac:task-list></td></tr>")
        content += ("<tr><td>SSL:</td><td><ac:task-list><ac:task><ac:task-id>"
                    "7</ac:task-id><ac:task-status>" + db_ssl + "</ac:task-status>"
                    "<ac:task-body><span>&nbsp;</span></ac:task-body></ac:task>"
                    "</ac:task-list></td></tr>")
        content += ("<tr><td>Oracle Schema CATS:</td><td><p>User: CATS</p><p>Password: CATS</p></td></tr>")
        content += ("<tr><td>Oracle Schema CATSCUST:</td><td><p>User: CATS</p><p>Password: CATS</p></td></tr>")
        content += ("<tr><td>Oracle Schema CATCON:</td><td><p>User: CATS</p><p>Password: CATS</p></td></tr>")
        content += ("<tr><td>Port:</td><td>" + str(db_port) + "</td></tr>")
        content += ("<tr><td>SID:</td><td>" + db_sid + "</td></tr>")
        content += ("<tr><td>Tablespace Name:</td><td>" + undef + "</td></tr>")
        content += ("<tr><td>TEMP Tablespace Name:</td><td>" + undef + "</td></tr>")
        content += ("<tr><td>Version:</td><td>" + undef + "</td></tr>")
    else:
        content += ("<th>" + undef_err + "</th></tr>")

    content += ("</tbody></table>")
    content += ("<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>")

    qr_url = ("<img src=\\\"http://api.qrserver.com/v1/create-qr-code/?data=lb."
              "" + str(env_id) + ".skytap.fulcrum.net:" + str(port_api) + ":1::"
              "" + env_name + "&amp;size=150x150\\\" />")

    # The qr_url in json_info will have "extra" escape chars (backslashes), but
    # it is included in json_info just in case.
    json_info["qr_url"] = qr_url

    content += ("<table><tbody><tr><th><p>QR Code for Configuration:</p><p>"
                "(Android only)</p></th><th>" + qr_url + "</th></tr></tbody>"
                "</table><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p><"
                "/ac:layout-cell></ac:layout-section></ac:layout>")

    content = clean_string(content)

    # -------------------------------------------------------------------------

    feedback, json_info = write_page.create(env_name, str(parent_id), content, json_info)

    with open("JSONS/" + env_id + ".json", "w") as file:
        json.dump(json_info, file)

    return feedback, env_name

