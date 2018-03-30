import commands
import json
import pyconfluence as pyco
import skytap
from jinja2 import Template

def list_garbage():
    """Display list of garbage DNS names."""

    space = "AutoDocs"

    aws_list = []
    skytap_list = []
    final_list = []

    status, output = commands.getstatusoutput("aws route53 "
                                              "list-resource-record-sets "
                                              "--hosted-zone-id "
                                              "/hostedzone/Z2M6JEL5C4DYRL")

    all_dns = json.loads(output)

    for record in all_dns["ResourceRecordSets"]:
        last_dash = record["Name"].rfind("-")
        dns_id = record["Name"][last_dash+1:-20]

        try:
            if int(dns_id) not in aws_list:
                aws_list.append(int(dns_id))
        except ValueError:
            continue

    envs = skytap.Environments()

    for e in envs:
        skytap_list.append(int(e.id))

    for i in aws_list:
        if i not in skytap_list:
            final_list.append(i)

    with open("update_scripts/update_dns_dumpster/dumpster.html", "r") as f:
        t = Template(f.read())

    content = "At the time being AWS DNS entries are not being disposed of properly. IDs for entries will be listed below.<br/>"

    for i in final_list:
        content += t.render(id=str(i))

    if content.strip() == pyco.get_page_content(pyco.get_page_id("AWS DNS Dumpster", space)).strip():
        print ("Content has not changed; skipping update.")
        return
    else:
        print pyco.edit_page(pyco.get_page_id("AWS DNS Dumpster", space), "AWS DNS Dumpster", space, content)


if __name__ == "__main__":
    list_garbage()
