import commands
import json
import pyconfluence as pyco
import skytap
import skytapdns

envs = skytap.Environments()

env_ids = []

status, output = commands.getstatusoutput("aws route53 list-resource-record-sets --hosted-zone-id /hostedzone/ZXN2JBL17W6BS")

data = json.loads(output)

for cur_env in data["ResourceRecordSets"]:
    if ".skytap.fulcrum.net." not in cur_env["Name"]:
        continue
    id = cur_env["Name"][(cur_env["Name"].find(".skytap.fulcrum.net.") - 7):(cur_env["Name"].find(".skytap.fulcrum.net."))]

    if id not in env_ids:
        env_ids.append(id)

print env_ids

print len(env_ids)

exit()

for e in envs:
    print ("Resetting " + e.name)
    pyco.delete_page_full(pyco.get_page_id(e.name, "AutoDocs"))
    skytapdns.recreate_all_vm_dns(e, True)

