
def create(data, parentID):
    """Create environment wiki page."""
    import json
    import os
    import write_page

    # Making a json containing important information. This will be stored in a
    # file in JSONS directory and used to perform various functions related to
    # Wiki Keeper.
    json_info = "{"

    # -------------------------------------------------------------------------

    undef = "Unavailable"
    undefErr = "Unavailable: data missing"

    with open("content_template_1.txt", "r") as file:
        toRead = file.read().replace('\n', '')

    env_id = data["id"]
    env_name = data["name"]
    config_url = data["url"]
    puppet_enabled = undef
    admin_access = undef
    user_access = undef

    content = (toRead % (config_url, config_url, undef, undef, undef))

    json_info += "\"id\": " + env_id + ", "

    json_info += "\"config_url\": \"" + config_url + "\", "

    with open("content_template_2.txt", "r") as file:
        toRead = file.read().replace('\n', '')

    json_info += "\"vms\": ["

    for i in data["vms"]:
        vm_name = i["interfaces"][0]["hostname"]
        base_url = "https://" + i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"]
        content += (toRead % (vm_name, base_url + "/cats/",
                              base_url + "/cats/",
                              vm_name, base_url + ":8443/cats/",
                              base_url + ":8443/cats/",
                              vm_name, base_url + ":8444/cats/",
                              base_url + ":8444/cats/",
                              vm_name, base_url + ":8445/cats/",
                              base_url + ":8445/cats/"))

        json_info += "{\"vm_name\": \"" + i["interfaces"][0]["hostname"] + "\", "
        json_info += "\"vm_ip\": \"" + i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"] + "\", "
        json_info += "\"vm_id\": " + i["id"] + "}, "

    json_info = json_info[:-2]
    json_info += "], "

    with open("content_template_3.txt", "r") as file:
        toRead = file.read().replace('\n', '')

    content += (toRead % (undef, undef, undef, undef))

    with open("content_template_4.txt", "r") as file:
        toRead = file.read().replace('\n', '')

    json_info += "\"vm_ports\": ["

    for i in data["vms"]:
        vm_name = i["interfaces"][0]["hostname"]
        ip = i["interfaces"][0]["nat_addresses"]["vpn_nat_addresses"][0]["ip_address"]

        json_info += "{\"vm_name\": \"" + i["interfaces"][0]["hostname"] + "\", "

        try:
            internal_port = str(i["interfaces"][0]["services"][0]["internal_port"])
            json_info += "\"internal_port\": " + str(i["interfaces"][0]["services"][0]["internal_port"]) + ", "
        except IndexError:
            internal_port = undefErr

        try:
            external_port = str(i["interfaces"][0]["services"][0]["external_port"])
            json_info += "\"external_port\": " + str(i["interfaces"][0]["services"][0]["external_port"]) + "}, "
        except IndexError:
            external_port = undefErr
            json_info = json_info[:-2]
            json_info += "}, "

        content += (toRead % (vm_name, ip, vm_name,
                              "https://" + ip + ":8446/catsmob/",
                              "https://" + ip + ":8446/catsmob/",
                              vm_name, internal_port,
                              vm_name, external_port))
    json_info = json_info[:-2]
    json_info += "], "

    with open("content_template_5.txt", "r") as file:
        toRead = file.read().replace('\n', '')

    qr_url = ("<img src=\\\"http://api.qrserver.com/v1/create-qr-code/?data=lb."
              "" + env_id + ".skytap.fulcrum.net:8446:1::" + env_name + ""
              "&amp;size=150x150\\\" />")

    content += (toRead % (undef, qr_url, undef, undef, undef, undef, undef,
                          undef, undef, undef, undef, undef, undef, undef,
                          undef, undef, undef, env_id))

    with open("JSONS/" + env_id + ".json", "w") as file:
        file.write(json_info)

    # -------------------------------------------------------------------------

    feedback, json_info = write_page.create(env_name, str(parentID),
                                            content, json_info)

    json_info = json_info[:-2]
    json_info += "}"

    with open("JSONS/" + env_id + ".json", "w") as file:
        file.write(json_info)

    with open("allSkytapIDs.txt", "a") as file:
            file.write(str(env_id) + "\n")

    return feedback, env_name

