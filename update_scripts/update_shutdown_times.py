from jinja2 import Template
import pyconfluence as pyco


def improve_storage(storage):
    """Get better string depicting storage."""

    sizes = ["KB", "MB", "GB", "TB", "uhhh...PB?"]

    cur_size = 0

    while storage > 1024:
        storage = storage / 1024
        cur_size += 1

    return (str(storage) + " " + sizes[cur_size])


def start(envs, config_data):
    """Start writing the environment shutdown times page."""

    space = config_data["space"]

    environments = ""
    environments_wo = ""  # For "Environments w/o Shutdown Times" page
    comment = ("Below are all environments followed by the amount of days of "
               "remaining until suspension, and the time of day (UTC) at which "
               "suspension occurs.")
    comment_wo = ("Below are all environments that are not automatically "
                  "shutting down. In order for an environment to shut down "
                  "properly, it must be given an environment_delay number "
                  "and an environment_shutdown number in its metadata.")

    for e in envs:
        print ("Updating for " + e.name + "...")
        name = e.name
        svms = e.svms
        storage = improve_storage(e.storage)

        if e.runstate == "running":
            status = "Ok-icon-small.png"
        elif e.runstate == "stopped" or e.runstate == "suspended":
            status = "Close-2-icon-small.png"
        else:
            status = "Lamp-icon.png"

        if "shutdown_delay" in e.user_data:
            shutdown_delay = str(e.user_data.shutdown_delay) + " days"
        else:
            shutdown_delay = "-"

        if "shutdown_time" in e.user_data and e.user_data.shutdown_time != "-":
            shutdown_time = str(e.user_data.shutdown_time) + ":00 UTC"
        else:
            shutdown_time = "-"

        if shutdown_delay == "-":
            color = "Grey"
        elif shutdown_delay == "0 days":
            color = "Red"
        elif shutdown_delay == "1 days" or shutdown_delay == "2 days":
            if shutdown_delay == "1 days":
                shutdown_delay = "1 day"
            color = "Yellow"
        else:
            color = "Green"

        if shutdown_time == "-":
            color2 = "Grey"
        else:
            color2 = "Blue"

        if shutdown_delay == "-" or shutdown_time == "-":
            with open("update_scripts/update_shutdown_times_html/environment_wo.html", "r") as f:
                t = Template(f.read())
            environments_wo += t.render(name=name, svms=svms, storage=storage).strip("\n")
            continue
        else:
            with open("update_scripts/update_shutdown_times_html/environment.html", "r") as f:
                t = Template(f.read())

        environments += t.render(status=status, name=name, color=color,
                                 days=shutdown_delay, color2=color2,
                                 time_utc=shutdown_time, svms=svms,
                                 storage=storage).strip("\n")

    with open("update_scripts/update_shutdown_times_html/template.html", "r") as f:
        t = Template(f.read())

    with open("update_scripts/update_shutdown_times_html/info.html", "r") as f:
        info = f.read()

    content = t.render(comment=comment, info=info,
                       environments=environments).strip("\n")

    with open("update_scripts/update_shutdown_times_html/template_wo.html", "r") as f:
        t = Template(f.read())

    content_wo = t.render(comment=comment_wo,
                          environments=environments_wo).strip("\n")

    print content

    print pyco.edit_page(pyco.get_page_id("Environment Shutdown Times", space),
                         "Environment Shutdown Times", space, content)

    print content_wo

    print pyco.edit_page(pyco.get_page_id("Environments w/o Shutdown Times", space),
                         "Environments w/o Shutdown Times", space, content_wo)

