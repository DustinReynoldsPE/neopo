import os
import shutil

import cache

# Load a script into the scripts directory
def load(args):
    try:
        scriptPath = args[2]
    except IndexError:
        print("You must specify a script file!")
        exit(1)

    shutil.copyfile(scriptPath, os.path.join(cache.SCRIPTS_DIR, os.path.basename(scriptPath)))
    print("Copied", scriptPath, "into", cache.SCRIPTS_DIR)

# Wrapper for [script]
def script(args):
    try:
        name = args[2]
    except IndexError:
        print("You must supply a script name!")
        exit(1)

    scriptPath = os.path.join(cache.SCRIPTS_DIR, name)

    try:
        with open(scriptPath, "r") as script:
            for line in script.readlines():

                if line.startswith("#"):
                    continue

                process = line.split()
                process.insert(0, args[0])

                if len(process) > 1:
                    print(process)
                    try:
                        cache.commands[process[1]](process)
                    except KeyError:
                        print("Invalid command!")
                        exit(1)

    except FileNotFoundError:
        print("Could find script!")