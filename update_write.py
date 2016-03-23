"""Write wiki pages of environments which currently have none."""

import confy_actions as confy
import build_page
import copy
import json
import skytap


def start(envs):
    """Write all remaining pages of environments not currently listed."""

    # Put the parent page information here.
    space = "AutoDocs"
    parent_id = 70385685

    # Just counting up the total number, for stats
    env_all = 0
    env_tried = 0
    env_written = 0
    env_failed = 0

    for e in envs:
        env_all += 1
        if (not confy.page_exists(e.name + " -- AutoDocs", space) and
                not e.name.startswith("VZW")):
            env_tried += 1

            content = build_page.build_env(e)
            try:
                result = json.loads(confy.create_page(e.name + " -- AutoDocs",
                                    parent_id, space, content))
            except TypeError:
                # Can't parse this because of "oops!" message, just continue
                env_failed += 1
                continue

            new_envs = skytap.Environments()
            new_e = new_envs[e.id]

            try:
                print ("checking if create_page worked...")
                page_id = result["id"]
                print ("it did...")

                for v in new_e.vms:
                    print ("trying " + v.name)
                    hostname, content = build_page.build_vm(v)

                    confy.create_page(hostname + " - " + v.name + " - " + new_e.name + " -- AutoDocs", page_id, space, content)
                    print ("it worked!")

                env_written += 1
            except (TypeError, KeyError):
                env_failed += 1

            if env_tried > 20:
                break

    print ("Total environments: " + str(env_all))
    print ("Total environments tried: " + str(env_tried))
    print ("Total environments written: " + str(env_written))
    print ("Total environments failed: " + str(env_failed))

