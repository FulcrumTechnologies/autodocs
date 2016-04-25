import pyconfluence as pyco
import skytap


def start(envs, config_data):
    """Print all VZW environments with published services to a page."""
    space = config_data["space"]
    other_docs_id = config_data["other_docs_id"]

    content = "Any and all VZW environments with published services will be listed below.<br/>"

    for e in envs:
        env_found = False
        if e.name.startswith("VZW"):
            for v in e.vms:
                for i in v.interfaces:
                    for s in i.services:
                        content += "<p>"
                        content += "<ac:link><ri:page ri:content-title=\"" + e.name + "\" /><ac:plain-text-link-body><![CDATA[" + e.name + "]]></ac:plain-text-link-body></ac:link>"
                        content += "</p>"
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
        print pyco.edit_page(76318788, "VZW Published Services", "AutoDocs", content)

