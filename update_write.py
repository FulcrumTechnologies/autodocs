"""Write wiki pages of environments which currently have none.

"""

import json


def start(envs):
    """Write all remaining pages of environments not currently listed."""

    env_all = 0

    # Count up total so we have completetion dialogue (1/95, 2/95, etc.)
    for e in envs:
        env_all += 1

    print ("Total environments: " + str(env_all))

