"""Write wiki pages of environments which currently have none."""

import confy_actions as confy
import build_page
import json


def start(envs):
    """Write all remaining pages of environments not currently listed."""

    space = "AutoDocs"
    parent_id = 68059270

    # Just counting up the total number, for stats
    env_all = 0
    env_tried = 0
    env_written = 0
    # for e in envs:
    #     env_all += 1

    for e in envs:
        if (not confy.page_exists(e.name + " -- AutoDocs", space) and
                not e.name.startswith("VZW")):
            env_tried += 1

            content = build_page.build_env(e)

            confy.create_page(e.name + " -- AutoDocs", parent_id, space, content)

            if env_tried > 5:
                return

    # print ("Total environments: " + str(env_all))
    print ("Total environments tried: " + str(env_tried))
    print ("Total environments written: " + str(env_written))

