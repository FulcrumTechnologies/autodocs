# Required: install cli53. Github repo: https://github.com/barnybug/cli53

import commands
import json
import pyconfluence as pyco
import time


def recreate_all_vm_dns(e, create):
    """Recreate DNS record sets and CNAMEs belonging to enviroment VMs.

    Parameters:
    e = Skytap Environment object.
    create = if False, end the function after deletion.
    """

    vm_hostname = "error"

    print ("Managing DNS settings for " + e.name + "...")

    for v in e.vms:
        vm_ip_us = None
        vm_ip_india = None
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

        dns_name = (vm_hostname + "-" + str(e.id) + ".skytap")

        status, output = commands.getstatusoutput("aws route53 "
                                                  "list-resource-record-sets "
                                                  "--hosted-zone-id "
                                                  "/hostedzone/Z2M6JEL5C4DYRL")
        print ("Obtained record sets...")

        data = json.loads(output)

        for rrs in data["ResourceRecordSets"]:
            break
            if rrs["ResourceRecords"][0]["Value"] == (dns_name + ".skytap.fulcrum.net."):
                cname = rrs["Name"].replace(".fulcrum.net.", "")
                status, output = commands.getstatusoutput("cli53 rrdelete "
                                                          "Z2M6JEL5C4DYRL "
                                                          "" + cname + " CNAME")
                print ("Deleted CNAME: " + cname + ".skytap.fulcrum.net")

        # status, output = commands.getstatusoutput("cli53 rrdelete Z2M6JEL5C4DYRL"
        #                                           " " + dns_name + " A")

        # print ("Deleted record set: " + dns_name + ".skytap.fulcrum.net")

        # If variable "create" is True, then do the second phase
        if not create:
            return
        
        if vm_ip_us:
            created = False
            quit_count = 0
            while not created:
                status, output = commands.getstatusoutput("cli53 rrcreate "
                                                          "Z2M6JEL5C4DYRL \'"
                                                          "" + vm_hostname + "-"
                                                          "" + str(e.id) + ""
                                                          " 3600 A " + vm_ip_us + ""
                                                          "\'")
                print ("Created. Checking...")
                time.sleep(3)
                status, output = commands.getstatusoutput("aws route53 "
                                                          "list-resource-record-sets "
                                                          "--hosted-zone-id "
                                                          "/hostedzone/Z2M6JEL5C4DYRL")
                data = json.loads(output)

                for rrs in data["ResourceRecordSets"]:
                    if (rrs["ResourceRecords"][0]["Value"] == (vm_ip_us) and
                            rrs["Name"] == vm_hostname + "-" + str(e.id) + ".skytap.fulcrum.net."):
                        created = True
                        print ("Created record set: " + vm_hostname + "-" + str(e.id) + ".skytap.fulcrum.net")

                quit_count += 1

        elif vm_ip_india:
            created = False
            quit_count = 0
            while not created:
                status, output = commands.getstatusoutput("cli53 rrcreate "
                                                          "Z2M6JEL5C4DYRL \'"
                                                          "" + vm_hostname + "-"
                                                          "" + str(e.id) + ""
                                                          " 3600 A " + vm_ip_india + ""
                                                          "\'")
                print ("Created. Checking...")
                time.sleep(3)
                status, output = commands.getstatusoutput("aws route53 "
                                                          "list-resource-record-sets "
                                                          "--hosted-zone-id "
                                                          "/hostedzone/Z2M6JEL5C4DYRL")
                data = json.loads(output)

                for rrs in data["ResourceRecordSets"]:
                    if (rrs["ResourceRecords"][0]["Value"] == (vm_ip_india) and
                            rrs["Name"] == vm_hostname + "-" + str(e.id) + ".skytap.fulcrum.net."):
                        created = True
                        print ("Created record set: " + vm_hostname + "-" + str(e.id) + ".skytap.fulcrum.net")

                quit_count += 1

        env_dns_alias = None

        if "env_dns_alias" in e.user_data:
            env_dns_alias = e.user_data.env_dns_alias

        if env_dns_alias:
            created = False
            quit_count = 0
            while not created:
                status, output = commands.getstatusoutput("cli53 rrcreate "
                                                          "Z2M6JEL5C4DYRL \'"
                                                          "" + vm_hostname + "-"
                                                          "" + env_dns_alias + ""
                                                          " 3600 CNAME "
                                                          "" + vm_hostname + "-"
                                                          "" + str(e.id) + "\'")
                time.sleep(1)
                status, output = commands.getstatusoutput("aws route53 "
                                                          "list-resource-record-sets "
                                                          "--hosted-zone-id "
                                                          "/hostedzone/Z2M6JEL5C4DYRL")
                data = json.loads(output)

                for rrs in data["ResourceRecordSets"]:
                    if ((vm_hostname + "-" + str(e.id) + ".skytap.fulcrum.net").lower() in rrs["ResourceRecords"][0]["Value"] and
                            (vm_hostname + "-" + env_dns_alias + ".skytap.fulcrum.net").lower() in rrs["Name"]):
                        created = True
                        print ("Created CNAME: " + vm_hostname + "-" + env_dns_alias + ".skytap.fulcrum.net")

                quit_count += 1


def delete_listed_dns(name):
    """Delete DNS names as listed in a Confluence page."""
    to_delete = []
    to_delete_cname = []

    content = pyco.get_page_content(pyco.get_page_id(name, "AutoDocs"))
    env_id = content[content.find("Environment ID: ")+16:content.find("Environment ID: ")+23]

    cname = None

    if "Grey</ac:parameter><ac:parameter ac:name=\"title\">" in content:
        cname = content[content.find("Grey</ac:parameter><ac:parameter ac:name=\"title\">")+49:content.find("</ac:parameter></ac:structured-macro></p><p>&nbsp;</p><p><strong>Additional Details")]

    children = json.loads(pyco.get_page_children(pyco.get_page_id(name, "AutoDocs")))
    for vm in children["results"]:
        to_delete.append(vm["title"][:vm["title"].find(" - ")] + "-" + str(env_id) + ".skytap")
        if cname:
            to_delete_cname.append(vm["title"][:vm["title"].find(" - ")] + "-" + cname + ".skytap")

    for vm in to_delete:
        status, output = commands.getstatusoutput("cli53 rrdelete Z2M6JEL5C4DYRL"
                                                  " " + vm + " A")

    for vm in to_delete_cname:
        status, output = commands.getstatusoutput("cli53 rrdelete "
                                                  "Z2M6JEL5C4DYRL "
                                                  "" + vm + " CNAME")

