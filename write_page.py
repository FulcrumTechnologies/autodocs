
def get_cfg():
    """Return config.yml as a yaml object."""
    try:
        import yaml
    except ImportError:
        sys.stderr.write("You do not have the 'yaml' module installed. "
                         "Please see http://pyyaml.org/wiki/PyYAMLDocumentation"
                         " for more information.")
        exit(1)

    try:
        f = open("config.yml")
        config_data = yaml.safe_load(f)
        f.close()
    except IOError:
        sys.stderr.write("There is no config.yml in the directory. Create one "
                         "and then try again.\nFor reference, check config_"
                         "template.yml and follow the listed guidelines.\n")
        exit(1)
    return config_data


def create(pageName, parentID, pageContent, json_info):
    """Takes relevant data and uses it to create environment or vm page."""
    import json
    import os

    config_data = get_cfg()

    # Create variables from config
    location = config_data["wiki_url"]
    username = config_data["wiki_user"]
    password = config_data["wiki_pass"]
    spaceKey = config_data["wiki_space"]
    envParent = config_data["wiki_parent"]

    # ------------- Create page with gathered initial information -------------

    if parentID == envParent:
        print "\nWriting new environment page: " + pageName
    else:
        print "\nWriting new VM page: " + pageName

    curlCmd = ("curl -u " + username + ":" + password + " -X POST -H \'Content"
               "-Type: application/json\' -d\'{\"type\": \"page\",\"title\": "
               "\"" + pageName + "\",\"ancestors\": [{\"id\": "
               "" + parentID + "}],\"space\": {\"key\": \"" + spaceKey + "\""
               "},\"body\": {\"storage\": {\"value\": \"" + pageContent + "\""
               ",\"representation\": \"storage\"}}}\' " + location + " | "
               "python -mjson.tool > temp.json")

    output = os.system(curlCmd)

    with open("temp.json") as file:
        data = json.load(file)

    # For use with purge_all_pages.py. Also checks if page was actually created
    try:
        with open("allPageIDs.txt", "a") as file:
            file.write(str(data["id"]) + "\n")

        json_info["page_id"] = data["id"]
    except KeyError as e:
        print ("Something went wrong; page was not generated. "
               "Error message returned: " + str(e))
        with open("temp.json", "r") as file:
            print file.read()
        return 999

    # Empties temp.json
    open("temp.json", 'w').close()

    return data["id"], json_info

