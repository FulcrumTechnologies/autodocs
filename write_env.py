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
    str = str.replace("\"", "\\\"")
    str = str.replace("\\\\\"", "\\\"")

    return str


def create(data, parent_id):
    """Create environment wiki page."""

    print ("Writing content..."),

    # Making a json containing important information. This will be stored in a
    # file in JSONS directory and used to perform various functions.
    json_info = {}

    # Placeholder variables.
    undef = "Unavailable"
    undef_err = "Unavailable: data missing"

    env_id = data["id"]
    env_name = clean_string(data["name"])

    config_url = data["url"]
    dash_url = "http://dashboard.fulcrum.net/" + env_id
    puppet_enabled = undef
    admin_access = undef
    user_access = undef

    # Exceptions are made when dealing with Verizon servers.
    if env_name.startswith("VZW"):
        url = "http://"
        port_home = 8001
        port_reports = 8003
        port_services = 8004
        port_mob = 8002
        mob_end = "cats"
    else:
        url = "https://"
        port_home = 8443
        port_reports = 8444
        port_services = 8445
        port_mob = 8446
        mob_end = "catsmob"

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

    storage_dir = "storage/"

    # If there is data in storage, use that instead of default info.
    if os.path.isfile(storage_dir + env_id + ".json"):
        stored = []

        # Make a JSON out of file info
        with open(storage_dir + env_id + ".json") as f:
            for line in f:
                stored.append(json.loads(line))
        comment = stored[0]["comment"]
        user = stored[0]["user"]
        password = stored[0]["password"]
        mob_ver = stored[0]["mob_ver"]
        apk_build = stored[0]["apk_build"]
        war_build = stored[0]["war_build"]
    else:
        comment = ("[Add any miscellaneous notes here. This box, along with "
                   "information entered into fields denoted by an asterisk *, "
                   "will be preserved through future updates.]")
        user = "?"
        password = "?"
        mob_ver = "?"
        apk_build = "?"
        war_build = "?"

    # First block of xhtml.
    # "content" will be affixed with vm_content and lb_content later on.
    content = ("<ac:layout><ac:layout-section ac:type=\\\"two_equal\\\"><ac:lay"
               "out-cell><p>" + comment + "</p></ac:layout-cell><ac:layout"
               "-cell><p>&nbsp;</p></ac:layout-cell></ac:layout-section>")

    content += ("<ac:layout-section ac:type=\\\"two_equal\\\">")
    content += ("<ac:layout-cell>")

    vm_content = ""
    lb_content = ""
    has_app1 = ""

    # Loop through every VM and affix xhtml to vm_content.
    for i in data["vms"]:
        vm_name = i["name"]
        vm_hostname = i["interfaces"][0]["hostname"]
        vm_id = i["id"]
        vm_user = undef
        vm_pass = undef
        ssh_enabled = undef
        ssl_enabled = undef

        vm_ip_us = ""
        vm_ip_india = ""

        # Allocate correct IP addresses for US and India.
        try:
            # US = US, SG = India
            for k in i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"]:
                if (k["vpn_id"] == "vpn-3631944" or
                        k["vpn_id"] == "vpn-661182"):
                    vm_ip_us = k["ip_address"]
                elif k["vpn_id"] == "vpn-3288770":
                    vm_ip_india = k["ip_address"]
        except (KeyError, IndexError):
            vm_ip_us = i["interfaces"][0]["ip"]

        base_url_us = url + vm_ip_us
        base_url_india = url + vm_ip_india

        services = []

        # Create data in JSON for individual service information.
        for j in i["interfaces"][0]["services"]:
            new_service = {}
            new_service["internal_ip"] = vm_ip_us
            new_service["internal_port"] = str(j["internal_port"])
            new_service["external_ip"] = j["external_ip"]
            new_service["external_port"] = str(j["external_port"])
            services.append(new_service)

        new_vm = {}
        new_vm["vm_name"] = vm_name
        new_vm["vm_hostname"] = vm_hostname
        new_vm["vm_ip_us"] = vm_ip_us
        new_vm["vm_ip_india"] = vm_ip_india
        new_vm["vm_id"] = vm_id
        new_vm["vm_base_url_us"] = base_url_us
        new_vm["vm_base_url_india"] = base_url_india
        new_vm["vm_user"] = vm_user
        new_vm["vm_pass"] = vm_pass
        new_vm["vm_ssh_enabled"] = ssh_enabled
        new_vm["vm_ssl_enabled"] = ssl_enabled
        new_vm["services"] = services

        # pub_content holds information displayed at the end of the individual
        # VM blocks.
        pub_content = ""

        # Writing service information
        serv_count = 0
        if len(services) != 0:
            pub_content += ("<p><strong> - Published Services:</strong></p>")
            for j in services:
                serv_count += 1
                pub_content += ("<p style=\\\"margin-left: 30.0px;\\\">Internal Port " + j["internal_port"] + " mapped to " + j["external_ip"] + ":" + j["external_port"] + "<span style=\\\"line-height: 1.4285715;\\\">&nbsp;</span></p>")

        # Writing public IP information
        if i["interfaces"][0]["public_ips_count"] > 0:
            pub_content += ("<p><strong> - Public IP Addresses:</strong></p>")
            for k in i["interfaces"][0]["public_ips"]:
                addr = k["address"]
                pub_content += ("<p><ac:structured-macro ac:macro-id=\\\"d245b98a-9f3e-46d0-9684-e07e3830153f\\\" ac:name=\\\"expand\\\" ac:schema-version=\\\"1\\\">")
                pub_content += ("<ac:parameter ac:name=\\\"title\\\">")
                pub_content += ("https://" + addr + "/cats/")
                pub_content += ("</ac:parameter>")
                pub_content += ("<ac:rich-text-body>")

                pub_content += ("<p>Direct link: <a href=\\\"https://" + addr + "/cats/\\\">https://" + addr + "/cats/</a></p>")

                qrc = ("<img src=\\\"http://api.qrserver.com/v1/create-qr-code/?data=https://" + addr + "/cats/&amp;size=150x150\\\" />")

                pub_content += ("<p>" + qrc + "</p>")

                pub_content += ("</ac:rich-text-body></ac:structured-macro></p>")

        # This will hold main content for each VM block
        vm_info = []

        # If this VM isn't the load balancer...
        if vm_hostname != "lb":
            vm_content += ("<h2><strong style=\\\"line-height: 1.4285715;\\\">" + vm_hostname + " - " + vm_name + "</strong></h2>")
            vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">VM ID: " + vm_id + "</p>")

            # IPs should be displayed when...
            if vm_ip_us != "":
                vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">IP (US): " + vm_ip_us + "</p>")
            if vm_ip_india != "":
                vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">IP (India): " + vm_ip_india + "</p>")

            # Never write down URLs when a database
            if vm_hostname != "db":
                if vm_ip_us != "":

                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Web: <a href=\\\"" + base_url_us + ":" + str(port_home) + "/cats/\\\">" + base_url_us + ":" + str(port_home) + "/cats/</a></p>")
                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Reports: <a href=\\\"" + base_url_us + ":" + str(port_reports) + "/cats/\\\">" + base_url_us + ":" + str(port_reports) + "/cats/</a></p>")
                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Services: <a href=\\\"" + base_url_us + ":" + str(port_services) + "/cats/\\\">" + base_url_us + ":" + str(port_services) + "/cats/</a></p>")
                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Mobility: <a href=\\\"" + base_url_us + ":" + str(port_mob) + "/" + mob_end + "/\\\">" + base_url_us + ":" + str(port_mob) + "/" + mob_end + "/</a></p>")

                    if vm_ip_india != "":
                        vm_content += ("<p><ac:structured-macro ac:macro-id=\\\"d245b98a-9f3e-46d0-9684-e07e3830153f\\\" ac:name=\\\"expand\\\" ac:schema-version=\\\"1\\\">")
                        vm_content += ("<ac:parameter ac:name=\\\"title\\\">")
                        vm_content += ("India VPN details:")
                        vm_content += ("</ac:parameter>")
                        vm_content += ("<ac:rich-text-body>")

                        vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Web: <a href=\\\"" + base_url_india + ":" + str(port_home) + "/cats/\\\">" + base_url_india + ":" + str(port_home) + "/cats/</a></p>")
                        vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Reports: <a href=\\\"" + base_url_india + ":" + str(port_reports) + "/cats/\\\">" + base_url_india + ":" + str(port_reports) + "/cats/</a></p>")
                        vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Services: <a href=\\\"" + base_url_india + ":" + str(port_services) + "/cats/\\\">" + base_url_india + ":" + str(port_services) + "/cats/</a></p>")
                        vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Mobility: <a href=\\\"" + base_url_india + ":" + str(port_mob) + "/" + mob_end + "/\\\">" + base_url_india + ":" + str(port_mob) + "/" + mob_end + "/</a></p>")

                        vm_content += ("</ac:rich-text-body></ac:structured-macro></p>")
                elif vm_ip_india != "":
                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Web: <a href=\\\"" + base_url_india + ":" + str(port_home) + "/cats/\\\">" + base_url_india + ":" + str(port_home) + "/cats/</a></p>")
                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Reports: <a href=\\\"" + base_url_india + ":" + str(port_reports) + "/cats/\\\">" + base_url_india + ":" + str(port_reports) + "/cats/</a></p>")
                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Services: <a href=\\\"" + base_url_india + ":" + str(port_services) + "/cats/\\\">" + base_url_india + ":" + str(port_services) + "/cats/</a></p>")
                    vm_content += ("<p style=\\\"margin-left: 30.0px;\\\">CATS Mobility: <a href=\\\"" + base_url_india + ":" + str(port_mob) + "/" + mob_end + "/\\\">" + base_url_india + ":" + str(port_mob) + "/" + mob_end + "/</a></p>")

                # Add pub_content at the end.
                vm_content += pub_content

            if vm_hostname == "app1" or vm_hostname == "app":
                has_app1 = vm_ip_us
                if vm_ip_us == "":
                    has_app1 = vm_ip_india

        # Print this stuff if this VM is load balancer
        else:
            lb_content += ("<h2><strong style=\\\"line-height: 1.4285715;\\\">" + vm_hostname + " - " + vm_name + "</strong></h2>")
            lb_content += ("<p style=\\\"margin-left: 30.0px;\\\">VM ID: " + vm_id + "</p>")

            if vm_ip_us != "":
                lb_content += ("<p style=\\\"margin-left: 30.0px;\\\">IP (US): " + vm_ip_us + "</p>")
            if vm_ip_india != "":
                lb_content += ("<p style=\\\"margin-left: 30.0px;\\\">IP (India): " + vm_ip_india + "</p>")

            if vm_ip_us != "":
                lb_content += ("<p style=\\\"margin-left: 30.0px;\\\">Load Balancer URL (US): <a href=\\\"" + base_url_us + "/cats/\\\">" + base_url_us + "/cats/</a></p>")
            if vm_ip_india != "":
                lb_content += ("<p style=\\\"margin-left: 30.0px;\\\">Load Balancer URL (India): <a href=\\\"" + base_url_india + "/cats/\\\">" + base_url_india + "/cats/</a></p>")

            # Add pub_content at the end.
            lb_content += pub_content

        if vm_hostname == "db":
            # This data will be used shortly for creating the database table.
            db_exists = True
            db_id = vm_id
            db_ip_us = vm_ip_us
            db_ip_india = vm_ip_india
            db_user = vm_user
            db_pass = vm_pass
            db_ssh = ssh_enabled
            db_ssl = ssl_enabled
            oracle_user = "oracle"
            db_schema = "CATS"
            db_password = "CATS"
            db_sid = "orcl"
            oracle_port = "1521"

            # If there is a db vm, this information will be added to db dict.
            new_db["db_id"] = db_id
            new_db["db_ip_us"] = db_ip_us
            new_db["db_ip_india"] = db_ip_india
            new_db["db_user"] = db_user
            new_db["db_pass"] = db_pass
            new_db["db_ssh"] = db_ssh
            new_db["db_ssl"] = db_ssl
            new_db["db_schema"] = db_schema
            new_db["db_password"] = db_password
            new_db["db_sid"] = db_sid
            new_db["db_port"] = oracle_port

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
    content += ("<p>Environment ID: " + str(env_id) + "</p>")
    content += ("<p>Admin User*: " + user + "</p>")
    content += ("<p>Admin PW*: " + password + "</p>")
    content += ("<p>Skytap Environment: <a href=\\\"" + config_url + "\\\">" + config_url + "</a></p>")
    content += ("<p>Environment Dashboard: <a href=\\\"" + dash_url + "\\\">" + dash_url + "</a></p>")
    content += ("<p>&nbsp;</p>")

    content += ("<p><strong>Mobility Details:</strong></p>")
    content += ("<p>Version*: " + mob_ver + "</p>")
    content += ("<p>APK Build*: " + apk_build + "</p>")
    content += ("<p>WAR Build: " + war_build + "</p>")
    content += ("<p>&nbsp;</p>")

    if db_exists:
        content += ("<p><strong>Oracle DB Info</strong></p>")
        content += ("<ul><li>Oracle OS User: " + oracle_user + "</li>")
        if db_ip_us != "":
            content += ("<li>IP (US): " + db_ip_us + "</li>")
        if db_ip_india != "":
            content += ("<li>IP (India): " + db_ip_india + "</li>")
        content += ("<li>DB Schema: " + db_schema + "</li>")
        content += ("<li>DB Password: " + db_password + "</li>")
        content += ("<li>SID: " + db_sid + "</li>")
        content += ("<li>Port: " + oracle_port + "</li>")
        content += ("</ul>")

    content += ("<p>&nbsp;</p><p>&nbsp;</p>")

    if has_app1 != "":
        qr_url = ("<img src=\\\"http://api.qrserver.com/v1/create-qr-code/?data="
                  "" + has_app1 + ":" + str(port_mob) + ":1::"
                  "" + env_name + "&amp;size=150x150\\\" />")

        # The qr_url in json_info will have "extra" escape chars (backslashes),
        # but it is included in json_info just in case.
        json_info["qr_url"] = qr_url

        content += ("<table><tbody><tr><th><p>QR Code for app1:</p><p>"
                    "(Android only)</p></th><th>" + qr_url + "</th></tr></tbody>"
                    "</table><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>")

    content += ("</ac:layout-cell></ac:layout-section>")

    content += ("</ac:layout>")

    content = clean_string(content)

    # Temporary!
    if env_name.startswith("VZW"):
        content = ("Auto documentation for this, and all Verizon environments, "
                   "has been suspended due to security concerns until further "
                   "notice.<br/><br/>Please go to this environment on Skytap to"
                   " access information on this environment.")

    # -------------------------------------------------------------------------

    feedback, json_info = write_page.create(env_name + " -- ", str(parent_id), content, json_info)

    if feedback != 0:
        with open("JSONS/" + env_id + ".json", "w") as file:
            json.dump(json_info, file)

    # Temporary!
    if env_name.startswith("VZW"):
        feedback = 0

    return feedback, env_name
