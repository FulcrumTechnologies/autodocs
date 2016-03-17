import os
import skytap
import sys
import update_write

def start(args):
    """Redirect to update function based on args."""

    envs = skytap.Environments()

    if (args[1] == "write"):
        os.system("clear")
        print ("Writing wiki pages.")
        #update_write.start(envs)
    else:
        print ("Command not recognized.")

    print ("\n\nJob\'s done.\n")


if __name__ == '__main__':
    start(sys.argv)

