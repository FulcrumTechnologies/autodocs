"""Write wiki pages of environments which currently have none."""

import confy_actions as confy
import build_page
import json


def start(envs):
    """Write all remaining pages of environments not currently listed."""

    # Just counting up the total number, for stats
    env_all = 0
    env_tried = 0
    env_written = 0
    for e in envs:
        env_all += 1

    for e in envs:
        if not confy.page_exists(e.id):
            env_tried += 1

            print build_page.build_env(e)
            return

    print ("Total environments: " + str(env_all))
    print ("Total environments tried: " + str(env_tried))
    print ("Total environments written: " + str(env_written))
