import pyconfluence as pyco
import skytap


def start(envs, config_data):
    """Print all known aliases (in environment userdata) to a page."""
    space = config_data["space"]
    other_docs_id = config_data["other_docs_id"]

    content = ("<p>All variables with the name \"env_dns_alias\" will appear "
               "below, alongside details of their respective environments."
               "</p>")

    records = {}

    for e in envs:
        if "env_dns_alias" in e.user_data:
            content += "<p>"
            content += e.user_data.env_dns_alias
            content += " - <ac:link><ri:page ri:content-title=\"" + e.name + "\" /><ac:plain-text-link-body><![CDATA[" + e.name + "]]></ac:plain-text-link-body></ac:link>"
            content += "</p>"

            if e.user_data.env_dns_alias not in records:
                records[e.user_data.env_dns_alias] = [e.name]
            else:
                records[e.user_data.env_dns_alias].append(e.name)

    last_content = ""

    for alias, names in records.iteritems():
        if len(names) > 1:
            last_content += alias + "<br/>"
            for n in names:
                last_content += " - <ac:link><ri:page ri:content-title=\"" + n + "\" /><ac:plain-text-link-body><![CDATA[" + n + "]]></ac:plain-text-link-body></ac:link><br/>"
            last_content += "<br/>"

    if last_content != "":
        content += ("<br/><p>All environments with identical env_dns_alias "
                    "variable values will appear below.</p>")
        content += last_content

    print content

    try:
        pyco.delete_page(pyco.get_page_id("Environment DNS Aliases", space))
    except IndexError:
        # Page doesn't exist
        pass

    pyco.create_page("Environment DNS Aliases", other_docs_id, space, content)
