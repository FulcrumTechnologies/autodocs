import os
import skytap
import sys
import update_write


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

    if (args[1] == "write"):
        os.system("clear")
        print ("Writing wiki pages.")
        update_write.start(envs, config_data)
    if (args[1] == "india"):
        os.system("clear")
        print ("Writing India wiki page.")
        update_india.start(config_data)
    else:
        print ("Command not recognized.")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)
