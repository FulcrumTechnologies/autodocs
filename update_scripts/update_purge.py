import json
import pyconfluence as pyco
import skytap
import skytapdns


def start(envs, config_data):
    """Start purging environment documentation for nonexistent environments."""

    space = config_data["space"]
    parent_id = config_data["parent_id"]

    children = json.loads(pyco.get_page_children(parent_id))

    written = []

    for r in children["results"]:
        written.append(r["title"])

    existing = []

    for e in envs:
        existing.append(e.name)

    for w in written:
        if w not in existing:
            print ("Deleting " + w + "..."),
            try:
                pyco.delete_page_full(pyco.get_page_id(w, space))
                print ("done.")
            except ValueError:
                print ("cannot interact with pages whose names include \"+\".")

