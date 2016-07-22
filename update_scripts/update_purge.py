import json
import pyconfluence as pyco
import skytap
import skytapdns


def clean_name(name):
    """Clean name of environment."""
    return name.replace("+", "(and)").replace("/", "(slash)")


def start(envs, config_data):
    """Start purging environment documentation for nonexistent environments."""

    space = config_data["space"]
    parent_id = config_data["parent_id"]

    children = json.loads(pyco.get_page_children(parent_id))

    written = []

    for r in children["results"]:
        written.append(r["title"])

    existing = []
    existing_names = []

    for e in envs:
        existing.append(e)
        existing_names.append(clean_name(e.name))

    for w in written:
        if w not in existing_names:
            print ("Deleting " + w + "..."),
            try:
                pyco.delete_page_full(pyco.get_page_id(w, space))
                skytapdns.delete_listed_dns(w)
                print ("done.")
            except ValueError:
                print ("cannot interact with pages whose names include \"+\".")

