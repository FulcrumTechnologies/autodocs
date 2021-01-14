import os
import skytap
import sys
from update_scripts import update_aliases
from update_scripts import update_india
from update_scripts import update_write_SP
from update_scripts import update_purge
from update_scripts import update_services
from update_scripts import update_public_ips
from update_scripts import update_shutdown_times
from update_scripts import update_write

def write(args, envs, config_data, number, name=None):
    """Begin process of writing wiki pages."""
    os.system("clear")
    if len(args) < 3:
        if number == 1 or args[1] == "write":
            print ("Writing wiki pages.")
            update_write.start(envs, config_data)
            return
        elif number == 2:
            name = raw_input("Enter a single word. All environments with this "
                             "word in their title will be updated:")

    # If a name was not given by the user, establish the input arg as the name.
    if not name:
        name = args[2]

    print ("Writing wiki pages for all environments with \""
           "" + name + "\" in the name.")
    update_write.start(envs, config_data, name)


def purge(envs, config_data):
    """Begin process of purging pages for nonexistent environments."""
    os.system("clear")
    print ("Purging wiki pages for nonexistent environments.")
    update_purge.start(envs, config_data)


def htmlout(args, envs, config_data,number,name=None):
    """Begin process of writing wiki pages."""
    os.system("clear")
    if len(args) < 3:
        if args[1] == "htmlout":
            print ("Writing Individual wiki pages for upload to SharePoint.")
            update_write_SP.start(envs, config_data)
            return
        elif number == 9:
            name = raw_input("Enter a single word. All environments with this "
                             "word in their title will be updated:")

    # If a name was not given by the user, establish the input arg as the name.
    if not name:
        name = args[2]

    print ("Writing HTML pages for all environments with \""
           "" + name + "\" in the name.")
    update_write_SP.start(envs, config_data, name)




def india(envs, config_data):
    """Begin process of updating India environments page."""
    os.system("clear")
    print ("Writing India wiki page.")
    update_india.start(envs, config_data)


def services(envs, config_data):
    """Begin process of updating published services page."""
    os.system("clear")
    print ("Writing Services wiki page.")
    update_services.start(envs, config_data)


def ips(envs, config_data):
    """Begin process of updating public IPs page."""
    os.system("clear")
    print ("Writing Public IPs wiki page.")
    update_public_ips.start(envs, config_data)


def aliases(envs, config_data):
    """Begin process of updating DNS aliases page."""
    os.system("clear")
    print ("Writing Aliases wiki page.")
    update_aliases.start(envs, config_data)


def shutdown_times(envs, config_data):
    """Begin process of updating shutdown times pages."""
    os.system("clear")
    print ("Writing Shutdown Times wiki page.")
    update_shutdown_times.start(envs, config_data)


def start(args):
    """Redirect to update function based on input given."""

    # Get all environments from Skytap
    envs = skytap.Environments()

    # Import yaml and yada yada yada
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

    number = None

    # Welcome text, if user types "python update.py"
    if (len(args) == 1):
        args.append(None) # Putting a dummy element in args for later on
        options = 9 # Number of options available here
        os.system("clear")
        print ("Welcome to Autodocs!")
        print ("To run a function, please enter the appropriate number below.")
        print ("\n------------------\n")
        print ("1 - Update wiki pages and DNS settings")
        print ("2 - Update the wiki page and DNS settings of specific "
               "environment(s)")
        print ("3 - Purge wiki space of pages for nonexistent environments")
        print ("4 - Update India environments wiki page")
        print ("5 - Update published services wiki page")
        print ("6 - Update public IPs wiki page")
        print ("7 - Update DNS aliases wiki page")
        print ("8 - Update shutdown times wiki pages")
        print ("9 - Write HTML pages to post to SharePoint")
        print ("\n------------------\n")

        while not number:
            number = raw_input("Type the number of the function you wish to "
                               "run:")
            try:
                number = int(number)
                if number > options:
                    number = None
            except ValueError:
                print ("Dude.")
                number = None

    # Go to specific functions based on passed arguments
    # Ex. "python update.py write" or "python update.py services"
    if ((number == 1 or number == 2) or args[1] == "write"):
        write(args, envs, config_data, number)
    elif (number == 3 or args[1] == "purge"):
        purge(envs, config_data)
    elif (number == 4 or args[1] == "india"):
        india(envs, config_data)
    elif (number == 5 or args[1] == "services"):
        services(envs, config_data)
    elif (number == 6 or args[1] == "ips"):
        ips(envs, config_data)
    elif (number == 7 or args[1] == "aliases"):
        aliases(envs, config_data)
    elif (number == 8 or args[1] == "shutdown_times"):
        shutdown_times(envs, config_data)
    elif (number == 9 or args[1] == "htmlout"):
        htmlout(args, envs, config_data, number)
    else:
        print ("Command not recognized.")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)
