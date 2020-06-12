import os
import subprocess

# Parse the project path from the specified index and run a Makefile target
def buildCommand(command, index, args):
    import build
    verboseIndex = index
    project = None
    verbosityDict = {"-v": 1, "-q": -1}

    try:
        if not args[index].startswith("-"):
            project = os.path.abspath(args[index])
            verboseIndex += 1
        else:
            project = os.getcwd()
    except IndexError:
        project = os.getcwd()
        verboseIndex = index

    try:
        verbosityStr = args[verboseIndex]
        verbosity = verbosityDict[verbosityStr]
    except IndexError:
        verbosity = 0
    except KeyError:
        print("Invalid verbosity!")
        return

    try:
        build.build(project, command, False, verbosity)
    except FileNotFoundError:
        print("Invalid project!")

# Print help information directly from Makefile
def build_help():
    import build
    build.build(None, None, True, 0)

# Wrapper for [config/configure]
def configure_command(args):
    import build
    try:
        platform = args[2]
        version = args[3]
    except IndexError:
        print("You must supply platform and deviceOS version!")
        return
    try:
        projectPath = args[4]
    except IndexError:
        projectPath = os.getcwd()

    build.configure(projectPath, platform, version)

# Wrapper for [run]
def run_command(args):
    try:
        command = args[2]
    except IndexError:
        build_help()
        print("You must supply a Makefile target!")
        return

    buildCommand(command, 3, args)

# Wrapper for [create]
def create_command(args):
    import build
    try:
        projectPath = args[2]
    except IndexError:
        print("You must supply a path for the project!")
        return

    projectPath = os.path.abspath(projectPath)
    build.create(os.path.dirname(projectPath), os.path.basename(projectPath))

# Wrapper for [get]
def get_command(args):
    import install
    try:
        version = args[2]
        install.downloadFirmware(version)
    except IndexError:
        print("You must specify a deviceOS version!")

# More wrappers
def flash_command(args):
    buildCommand("flash-user", 2, args)
def compile_command(args):
    buildCommand("compile-user", 2, args)
def flash_all_command(args):
    buildCommand("flash-all", 2, args)
def clean_command(args):
    buildCommand("clean-user", 2, args)
def install_command(args):
    import install
    install.installOrUpdate(True)
def update_command(args):
    import install
    install.installOrUpdate(False)

# Iterate through all connected devices and run a command
def iterate_command(args):
    import cache
    tempEnv = os.environ.copy()
    cache.addToPath(tempEnv, cache.NEOPO_DEPS)

    process = ["particle", "serial", "list"]
    particle = subprocess.run(process, stdout=subprocess.PIPE,
                                        env=tempEnv,
                                        shell=cache.running_on_windows)

    devices = []
    
    for line in particle.stdout.splitlines()[1:]:
        words = line.decode("utf-8").split()
        device = words[-1]
        devices.append(device)

    del args[1]

    try:
        if args[1] == "iterate":
            print("Do not use `iterate` recursively!")
            return
        elif not args[1] in cache.iterable_commands.keys():
            print("Invalid command!")
            return
    except IndexError:
        print("You must supply a command to iterate with!")
        return

    for device in devices:
        print("DeviceID:", device)
        process = ["particle", "usb", "dfu", device]
        subprocess.run(process, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                env=tempEnv,
                                shell=cache.running_on_windows)

        cache.iterable_commands[args[1]](args)

# Print help information about the program
def print_help(args):
    print("""Usage: neopo [OPTIONS] [PROJECT] [-v/q]

Options:
    General Options:
        help
        install
        uninstall
        versions
        create <project>

    Build Options:
        compile/build [project] [-v/q]
        flash [project] [-v/q]
        flash-all [project] [-v/q]
        clean [project] [-v/q]

    Special Options:
        run <target> [project] [-v/q]
        configure <platform> <version> [project]

    Dependency Options:
        update
        get <version>
        """)

# Wrapper for [download-unlisted]
def downloadUnlisted_command(args):
    try:
        install.downloadUnlisted(args[2])
    except IndexError:
        print("You must specify a deviceOS version!")