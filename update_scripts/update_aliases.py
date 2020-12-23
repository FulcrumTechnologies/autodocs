import pyconfluence as pyco
import skytap
from jinja2 import Template


def clean_name(name):
    """Clean name of environment."""
    return name.replace("+", "(and)").replace("/", "(slash)")


def start(envs, config_data):
    """Print all known aliases (in environment userdata) to a page."""
    space = config_data["space"]
    other_docs_id = config_data["other_docs_id"]

    with open("update_scripts/update_aliases/header.html", "r") as f:
        t = Template(f.read())

    content = t.render()

    records = {}

    with open("update_scripts/update_aliases/alias.html", "r") as f:
        t = Template(f.read())

    # Get aliases from userdata and append to records
    for e in envs:
        if "env_dns_alias" in e.user_data:
            print ("Found alias: " + e.user_data.env_dns_alias + " - in " + clean_name(e.name))
            content += t.render(alias=e.user_data.env_dns_alias, name=clean_name(e.name))

            if e.user_data.env_dns_alias not in records:
                records[e.user_data.env_dns_alias] = [clean_name(e.name)]
            else:
                records[e.user_data.env_dns_alias].append(clean_name(e.name))

    # This contains the duplicate alias data
    end_content = ""

    # Find what environments, if any, have duplicate aliases
    for alias, names in records.iteritems():
        if len(names) > 1:
            print ("Found duplicate alias: " + alias)
            with open("update_scripts/update_aliases/dup_alias1.html", "r") as f:
                t = Template(f.read())
            with open("update_scripts/update_aliases/dup_alias2.html", "r") as f:
                t2 = Template(f.read())
            dups = ""
            for n in names:
                dups += t2.render(name=n)
            end_content += t.render(alias=alias, dups=dups)

    if end_content != "":
        with open("update_scripts/update_aliases/dup_alias_header.html", "r") as f:
            t = Template(f.read())
        content += t.render() + end_content

    print (content)

    if content.strip() == pyco.get_page_content(pyco.get_page_id("Environment DNS Aliases", space)).strip():
        print ("Content has not changed; skipping update.")
        return
    else:
        print (pyco.edit_page(pyco.get_page_id("Environment DNS Aliases", space), "Environment DNS Aliases", space, content))

