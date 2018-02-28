import os
import skytap
import sys
from update_scripts import update_aliases
from update_scripts import update_india
from update_scripts import update_purge
from update_scripts import update_services
from update_scripts import update_public_ips
from update_scripts import update_shutdown_times
from update_scripts import update_write


def start(args):
    """Redirect to update function based on args."""

    envs = skytap.Environments()

    try:
        import yaml
    except ImportError:
        sys.stderr.write("You do not have the 'yaml' module installed. "
                         "Please see http://pyyaml.org/wiki/PyYAMLDocumentation"
                         " for more information.")
        exit(1)

    try:
        f = open("config.yml")
        config_data = yaml.safe_load(f)
        f.close()
    except IOError:
        sys.stderr.write("There is no config.yml in the directory. Create one "
                         "and then try again.\nFor reference, check config_"
                         "template.yml and follow the listed guidelines.\n")
        exit(1)

    # Go to specific functions based on passed arguments
    # Ex. "python update.py write" or "python update.py services"
    if (args[1] == "write"):
        os.system("clear")
        if len(args) < 3:
            print ("Writing wiki pages.")
            update_write.start(envs, config_data)
        else:
            print ("Writing wiki pages for all environments with \""
                   "" + args[2] + "\" in the name.")
            update_write.start(envs, config_data, args[2].strip())
    elif (args[1] == "purge"):
        os.system("clear")
        print ("Purging wiki pages for nonexistent environments.")
        update_purge.start(envs, config_data)
    elif (args[1] == "india"):
        os.system("clear")
        print ("Writing India wiki page.")
        update_india.start(envs, config_data)
    elif (args[1] == "services"):
        os.system("clear")
        print ("Writing Services wiki page.")
        update_services.start(envs, config_data)
    elif (args[1] == "ips"):
        os.system("clear")
        print ("Writing Public IPs wiki page.")
        update_public_ips.start(envs, config_data)
    elif (args[1] == "aliases"):
        os.system("clear")
        print ("Writing Aliases wiki page.")
        update_aliases.start(envs, config_data)
    elif (args[1] == "shutdown_times"):
        os.system("clear")
        print ("Writing Shutdown Times wiki page.")
        update_shutdown_times.start(envs, config_data)
    else:
        print ("Command not recognized.")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)

