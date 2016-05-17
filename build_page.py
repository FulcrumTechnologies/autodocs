"""Builds the XHTML source that will become a Confluence page."""
import commands
from jinja2 import Template
import json
import skytapdns


def clean_string(text):
    """Clean a string up so it doesn't screw things."""
    text = text.replace("\'", "")

    return text


def build_lb(vm_hostname, vm_name, vm_id, vm_ip_us, vm_ip_india, origin_ip_us,
             origin_ip_india, pub_services, pub_ips):
    """Build load balancer HTML."""
    with open("build_html/lb_ip.html", "r") as f:
        t = Template(f.read())

    ip = build_ip(t, vm_ip_us, vm_ip_india, origin_ip_us, origin_ip_india, True,
                  False)

    with open("build_html/lb.html", "r") as f:
        t = Template(f.read())

    return t.render(hostname=vm_hostname, name=vm_name, id=vm_id, ip=ip,
                    pub_services=pub_services, pub_ips=pub_ips).strip("\n")


def build_db(vm_hostname, vm_name, vm_id, vm_ip_us, vm_ip_india, origin_ip_us,
             origin_ip_india, pub_services, pub_ips):
    """Build database HTML."""
    if vm_name.startswith("VZW"):
        is_vzw = True
    else:
        is_vzw = False

    with open("build_html/app_ip.html", "r") as f:
        t = Template(f.read())

    ip = build_ip(t, vm_ip_us, vm_ip_india, origin_ip_us, origin_ip_india, True,
                  is_vzw)

    with open("build_html/app.html", "r") as f:
        t = Template(f.read())

    return t.render(hostname=vm_hostname, name=vm_name, id=vm_id, ip=ip,
                    pub_services=pub_services, pub_ips=pub_ips).strip("\n")


def build_etl():
    """Build ETL DB HTML."""
    pass


def build_nfs():
    """Build NFS HTML."""
    pass


def build_app(vm_hostname, vm_name, vm_id, vm_ip_us, vm_ip_india, origin_ip_us,
              origin_ip_india, pub_services, pub_ips):
    """Build app/host/etc. HTML."""
    if vm_name.startswith("VZW"):
        is_vzw = True
    else:
        is_vzw = False

    with open("build_html/app_ip.html", "r") as f:
        t = Template(f.read())

    ip = build_ip(t, vm_ip_us, vm_ip_india, origin_ip_us, origin_ip_india,
                  False, is_vzw)

    with open("build_html/app.html", "r") as f:
        t = Template(f.read())

    return t.render(hostname=vm_hostname, name=vm_name, id=vm_id, ip=ip,
                    pub_services=pub_services, pub_ips=pub_ips).strip("\n")


def build_ip(t, vm_ip_us, vm_ip_india, origin_ip_us, origin_ip_india, is_short,
             is_vzw):
    """Build IP info HTML."""

    good_ip = ""

    if vm_ip_us != "":
        good_ip = vm_ip_us
        ip = t.render(loc="US", origin_ip=origin_ip_us, ip=vm_ip_us)
    elif vm_ip_india != "":
        good_ip = vm_ip_india
        ip = t.render(loc="India", origin_ip=origin_ip_india, ip=vm_ip_india)
    else:
        ip = ""
        good_ip = ip

    if not is_short:
        if not is_vzw:
            ports = ["8443", "8444", "8445", "8446"]
        else:
            ports = ["8001", "8003", "8004", "8002"]

        with open("build_html/web.html", "r") as f:
            t = Template(f.read())
        ip += t.render(protocol="https", port=ports[0], ip=good_ip)
        with open("build_html/reports.html", "r") as f:
            t = Template(f.read())
        ip += t.render(protocol="https", port=ports[1], ip=good_ip)
        with open("build_html/services.html", "r") as f:
            t = Template(f.read())
        ip += t.render(protocol="https", port=ports[2], ip=good_ip)
        with open("build_html/mobility.html", "r") as f:
            t = Template(f.read())
        ip += t.render(protocol="https", port=ports[3], ip=good_ip)

    return ip.strip("\n")


def build_pub_services(internal_port, external_ip, external_port):
    """Build published services HTML."""
    with open("build_html/pub_service_item.html", "r") as f:
        t = Template(f.read())
    return t.render(internal_port=internal_port, external_ip=external_ip,
                    external_port=external_port).strip("\n")


def build_pub_ips(addr):
    """Build public IPs HTML."""
    with open("build_html/pub_ip_item.html", "r") as f:
        t = Template(f.read())
    return t.render(pub_ip=addr).strip("\n")


def build_userdata(data):
    """Build userdata HTML."""
    userdata_html = ""

    with open("build_html/userdata_item.html", "r") as f:
        t = Template(f.read())

    if "shutdown_time" in data:
        userdata_html += t.render(key="shutdown_time",
                                  value=str(data.shutdown_time))
    if "shutdown_delay" in data:
        userdata_html += t.render(key="shutdown_delay",
                                  value=(data.shutdown_delay))

    if "env_dns_alias" in data:
        userdata_html += t.render(key="env_dns_alias",
                                  value=(data.env_dns_alias))

    with open("build_html/userdata.html", "r") as f:
        t = Template(f.read())

    return t.render(userdata_items=userdata_html)


def build_add_details(env_id, user, password):
    """Build Additional Details HTML."""
    with open("build_html/add_details.html", "r") as f:
        t = Template(f.read())

    return t.render(env_id=env_id, admin_user=user, admin_pass=password)


def build_mob_details(mob_ver, apk_build, war_build):
    """Build Additional Details HTML."""
    with open("build_html/mob_details.html", "r") as f:
        t = Template(f.read())

    return t.render(mob_version=mob_ver, apk_build=apk_build,
                    war_build=war_build)


def build_db_info(oracle_user, db_ip_us, db_ip_india, db_schema, db_password,
                  db_sid, oracle_port):
    """Build DB info HTML."""
    if db_ip_us != "":
        good_ip = db_ip_us
        loc = "US"
    elif db_ip_india != "":
        good_ip = db_ip_india
        loc = "India"
    else:
        return ""

    with open("build_html/db_info.html", "r") as f:
        t = Template(f.read())

    return t.render(os_user=oracle_user, loc=loc, db_ip=good_ip,
                    db_schema=db_schema, dp_pass=db_password, sid=db_sid,
                    db_port=oracle_port)


def build_env(e):
    """Build a Confluence page for an environment.

    This is pretty dirty and violates a few pep guidelines, most notably the
    80 character length rule.

    This function is a bit like Cthulhu. Keep trying to figure it out, and
    you'll go insane.

    Unlike Cthulhu, this function returns a big ball of XHTML that will serve as
    the Confluence page's code.
    """

    #print ("Writing content for environment..."),

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

    has_app1 = ""

    user = "?"
    password = "?"
    mob_ver = "?"
    apk_build = "?"
    war_build = "?"

    comment = ("Maintained by AutoDocs; any changes made on this page will be "
               "undone on the next iteration.")
    lb = ""
    apps = ""
    nfs = ""
    db = ""
    etl = ""
    userdata = ""
    db_info = ""
    qr = ""

    # Loop through every VM and affix xhtml to vm_content.
    for v in e.vms:
        vm_name = v.name

        vm_id = str(v.id)
        vm_user = undef
        vm_pass = undef
        ssh_enabled = undef
        ssl_enabled = undef

        vm_ip_us = ""
        vm_ip_india = ""

        count = 0

        services = []

        # Create data in JSON for individual service information.
        for i in v.interfaces:
            vm_hostname = i.hostname
            int_data = json.loads(i.json())
            try:
                for n in int_data["nat_addresses"]["vpn_nat_addresses"]:
                    if (n["vpn_id"] == "vpn-661182" or
                            n["vpn_id"] == "vpn-3631944"):
                        vm_ip_us = n["ip_address"]
                    elif n["vpn_id"] == "vpn-3288770":
                        vm_ip_india = n["ip_address"]
            except (KeyError, TypeError, IndexError):
                vm_ip_us = i.ip

            count = int(i.public_ips_count)
            public_ips = i.public_ips
            for s in i.services:
                #print ("checking out services...")
                new_service = {}
                try:
                    new_service["internal_ip"] = str(s.id)
                    new_service["internal_port"] = str(s.internal_port)
                    new_service["external_ip"] = str(s.external_ip)
                    new_service["external_port"] = str(s.external_port)
                    services.append(new_service)
                except AttributeError:
                    pass

        env_dns_alias = None

        if "env_dns_alias" in e.user_data:
            env_dns_alias = e.user_data.env_dns_alias

        origin_ip_us = ""
        origin_ip_india = ""

        if vm_ip_us != "":
            origin_ip_us = vm_ip_us
            if not env_dns_alias:
                vm_ip_us = "" + vm_hostname + "-" + str(env_id) + ".skytap.fulcrum.net"
            else:
                vm_ip_us = "" + vm_hostname + "-" + env_dns_alias + ".skytap.fulcrum.net"
        elif vm_ip_india != "":
            origin_ip_india = vm_ip_india
            if not env_dns_alias:
                vm_ip_india = "" + vm_hostname + "-" + str(env_id) + ".skytap.fulcrum.net"
            else:
                vm_ip_india = "" + vm_hostname + "-" + env_dns_alias + ".skytap.fulcrum.net"

        base_url_us = url + vm_ip_us
        base_url_india = url + vm_ip_india

        # Writing service information
        services_html = ""
        pub_services = ""
        if len(services) != 0:
            with open("build_html/pub_services.html", "r") as f:
                t = Template(f.read())
            for s in services:
                pub_services += build_pub_services(str(s["internal_port"]),
                                                   str(s["external_ip"]),
                                                   str(s["external_port"]))
            services_html = t.render(pub_services=pub_services)

        # Writing public IP information
        pub_ips_html = ""
        pub_ips = ""
        if count > 0:
            with open("build_html/pub_ips.html", "r") as f:
                t = Template(f.read())
            for k in public_ips:
                pub_ips += build_pub_ips(k["address"])
            pub_ips_html = t.render(pub_ips=pub_ips)

        # If this VM isn't the load balancer...
        if vm_hostname == "lb":
            lb_html = build_lb(vm_hostname, vm_name, vm_id, vm_ip_us,
                               vm_ip_india, origin_ip_us, origin_ip_india,
                               services_html, pub_ips_html)
        # Never write down URLs when a database
        elif vm_hostname == "db":
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

            db = build_db(vm_hostname, vm_name, vm_id, vm_ip_us,
                          vm_ip_india, origin_ip_us, origin_ip_india,
                          services_html, pub_ips_html)
        elif (vm_hostname == "etl" or vm_hostname == "etl-db"):
            etl = build_db(vm_hostname, vm_name, vm_id, vm_ip_us,
                           vm_ip_india, origin_ip_us, origin_ip_india,
                           services_html, pub_ips_html)
        elif vm_hostname == "nfs":
            nfs = build_db(vm_hostname, vm_name, vm_id, vm_ip_us,
                           vm_ip_india, origin_ip_us, origin_ip_india,
                           services_html, pub_ips_html)
        else:
            apps += build_app(vm_hostname, vm_name, vm_id, vm_ip_us,
                              vm_ip_india, origin_ip_us, origin_ip_india,
                              services_html, pub_ips_html)

        if vm_hostname == "app1" or vm_hostname == "app":
            has_app1 = vm_ip_us
            if vm_ip_us == "":
                has_app1 = vm_ip_india

    userdata = build_userdata(e.user_data)

    add_details = build_add_details(env_id, user, password)

    mob_details = build_mob_details(mob_ver, apk_build, war_build)

    if db_exists:
        db_info = build_db_info(oracle_user, db_ip_us, db_ip_india, db_schema,
                                db_password, db_sid, oracle_port)

    if has_app1 != "":
        with open("build_html/qr.html", "r") as f:
            t = Template(f.read())

        qr = t.render(vm_name="app1", ip=has_app1, port=str(port_mob),
                      env_name=env_name)

    # -------------------------------------------------------------------------

    with open("build_html/template.html", "r") as f:
        t = Template(f.read())

    content = t.render(comment=comment, lb=lb, apps=apps, nfs=nfs, db=db,
                       etl=etl, userdata=userdata, add_details=add_details,
                       mob_details=mob_details, db_info=db_info, qr=qr)

    return content


def build_vm(v):
    """Build a Confluence page for a VM.

    Just like build_env, this function is hard to look at.

    This function also returns XHTML that can be used to create the page in
    Confluence. It also returns the hostname out of necessity to win a battle
    with a notoriously evasive bug.
    """
    #print ("Writing content for VM...")

    vm_name = v.name
    vm_id = str(v.id)

    content = "<p>"

    content += ("ID: " + vm_id + "<br/><br/>")

    #content += ("Configuration URL: " + v.configuration_url + "<br/>")

    for i in v.interfaces:
        vm_hostname = i.hostname
        int_data = json.loads(i.json())

        content += ("<br/>")
        try:
            for n in int_data["nat_addresses"]["vpn_nat_addresses"]:
                if (n["vpn_id"] == "vpn-3631944" or
                        n["vpn_id"] == "vpn-661182"):
                    content += ("NAT IP (US): " + n["ip_address"] + "<br/>")
                elif n["vpn_id"] == "vpn-3288770":
                    content += ("NAT IP (India): " + n["ip_address"] + "<br/>")
        except (KeyError, IndexError):
            content += ("NAT IP (US): " + i.ip + "<br/>")

        content += ("Local IP: " + i.ip + "<br/>")

    content += ("<br/><br/>")

    content += ("<ac:structured-macro ac:name=\"iframe\" ac:schema-version=\"1\" ac:macro-id=\"1c30019c-dd2a-4c4c-bfa9-387ce00e1d4d\"><ac:parameter ac:name=\"src\"><ri:url ri:value=\"http://dashboard.fulcrum.net/" + vm_id + "\" /></ac:parameter><ac:parameter ac:name=\"width\">850</ac:parameter><ac:parameter ac:name=\"height\">535</ac:parameter><ac:rich-text-body><p>&nbsp;</p></ac:rich-text-body></ac:structured-macro>")

    content += ("</p>")

    return vm_hostname, content
