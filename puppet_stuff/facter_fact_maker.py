#! /bin/env python

# Used to generate facter facts based off information from Skytap. Put this
# where you put your facter fact generation scripts

import commands
import json
#import skytap

status, output = commands.getstatusoutput("curl -s http://192.168.1.254/skytap")

data = json.loads(output)

#envs = skytap.Environments()

#env = envs[env_id]

print "env_id=" + data["configuration_url"][-7:]
print "vm_name=" + data["name"]
print "vm_hostname=" + data["interfaces"][0]["hostname"]
print "vm_id=" + data["id"]
print "vm_ip=" + data["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"]
print "vm_vpn_id=" + data["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["vpn_id"]
