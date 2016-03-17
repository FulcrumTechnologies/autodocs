"""Builds the XHTML source that will become a Confluence page."""


def clean_string(str):
    """Clean up lone apostrophes and quotations in string."""
    str = str.replace("\'", "")
    str = str.replace("\"", "\\\"")
    str = str.replace("\\\\\"", "\\\"")

    return str


def build_env(e):
    """Build a Confluence page for an environment.

    This is pretty dirty and violates a lot of pep guidelines, most notably the
    80 character length rule. If you're having trouble understanding it, don't
    worry, that's normal. Feel free to rewrite this.

    Returns a big ball of XHTML that will serve as the Confluence page code.
    """

    print ("Writing content..."),

    # Making a json containing important information. This will be stored in a
    # file in JSONS directory and used to perform various functions.

    # Placeholder variables.
    undef = "Unavailable"
    undef_err = "Unavailable: data missing"

    env_id = str(e.id)
    env_name = clean_string(e.name)

    config_url = e.url
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

    db_exists = False
    db_id = undef

    comment = ("Maintained by AutoDocs; any changes made on this page will be "
               "undone on the next iteration.")
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
    for v in e.vms:
        vm_name = v.name

        for i in v.interfaces:
            vm_hostname = i.hostname

        vm_id = str(v.id)
        vm_user = undef
        vm_pass = undef
        ssh_enabled = undef
        ssl_enabled = undef

        vm_ip_us = ""
        vm_ip_india = ""

        for i in v.interfaces:
            vm_ip_us = i.ip

        base_url_us = url + vm_ip_us
        base_url_india = url + vm_ip_india

        services = []

        # Create data in JSON for individual service information.
        for i in v.interfaces:
            for s in i.services:
                new_service = {}
                new_service["internal_ip"] = vm_ip_us
                new_service["internal_port"] = str(j["internal_port"])
                new_service["external_ip"] = j["external_ip"]
                new_service["external_port"] = str(j["external_port"])
                services.append(new_service)

        # pub_content holds information displayed at the end of the individual
        # VM blocks.
        pub_content = ""

        # Writing service information
        serv_count = 0
        if len(services) != 0:
            pub_content += ("<p><strong> - Published Services:</strong></p>")
            for s in services:
                serv_count += 1
                pub_content += ("<p style=\\\"margin-left: 30.0px;\\\">Internal Port " + str(s.internal_port) + " mapped to " + str(s.external_ip) + ":" + str(s.external_port) + "<span style=\\\"line-height: 1.4285715;\\\">&nbsp;</span></p>")

        # # Writing public IP information
        # if i["interfaces"][0]["public_ips_count"] > 0:
        #     pub_content += ("<p><strong> - Public IP Addresses:</strong></p>")
        #     for k in i["interfaces"][0]["public_ips"]:
        #         addr = k["address"]
        #         pub_content += ("<p><ac:structured-macro ac:macro-id=\\\"d245b98a-9f3e-46d0-9684-e07e3830153f\\\" ac:name=\\\"expand\\\" ac:schema-version=\\\"1\\\">")
        #         pub_content += ("<ac:parameter ac:name=\\\"title\\\">")
        #         pub_content += ("https://" + addr + "/cats/")
        #         pub_content += ("</ac:parameter>")
        #         pub_content += ("<ac:rich-text-body>")
        #
        #         pub_content += ("<p>Direct link: <a href=\\\"https://" + addr + "/cats/\\\">https://" + addr + "/cats/</a></p>")
        #
        #         qrc = ("<img src=\\\"http://api.qrserver.com/v1/create-qr-code/?data=https://" + addr + "/cats/&amp;size=150x150\\\" />")
        #
        #         pub_content += ("<p>" + qrc + "</p>")
        #
        #         pub_content += ("</ac:rich-text-body></ac:structured-macro></p>")

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

        content += ("<table><tbody><tr><th><p>QR Code for app1:</p><p>"
                    "(Android only)</p></th><th>" + qr_url + "</th></tr></tbody>"
                    "</table><p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>")

    content += ("</ac:layout-cell></ac:layout-section></ac:layout>")

    content = clean_string(content)

    # Temporary!
    if env_name.startswith("VZW"):
        content = ("Auto documentation for this, and all Verizon environments, "
                   "has been suspended due to security concerns until further "
                   "notice.<br/><br/>Please go to this environment on Skytap to"
                   " access information on this environment.")

    # -------------------------------------------------------------------------

    return content