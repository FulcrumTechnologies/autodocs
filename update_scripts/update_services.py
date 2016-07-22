import pyconfluence as pyco
import skytap
from jinja2 import Template


def clean_name(name):
    """Clean name of environment."""
    return name.replace("+", "(and)").replace("/", "(slash)")


def start(envs, config_data):
    """Print all VZW environments with published services to a page."""
    space = config_data["space"]
    other_docs_id = config_data["other_docs_id"]

    content = "Any and all VZW environments with published services will be listed below.<br/>"

    with open("update_scripts/update_services/service.html", "r") as f:
        t = Template(f.read())

    for e in envs:
        env_found = False
        if clean_name(e.name).startswith("VZW"):
            for v in e.vms:
                for i in v.interfaces:
                    for s in i.services:
                        content += t.render(name=clean_name(e.name))
                        env_found = True
                        break
                    if env_found:
                        break
                if env_found:
                    break

    print content

    if content.strip() == pyco.get_page_content(pyco.get_page_id("VZW Published Services", space)).strip():
        print ("Content has not changed; skipping update.")
        return
    else:
        print pyco.edit_page(pyco.get_page_id("VZW Published Services", space), "VZW Published Services", space, content)

