import os
import platform
import json

import command




import script
import install
import build

# Global Variables
PARTICLE_DEPS = os.path.join(os.environ["HOME"], ".particle", "toolchains")
NEOPO_DEPS = os.path.join(os.environ["HOME"], ".neopo")
CACHE_DIR = os.path.join(NEOPO_DEPS, "cache")
SCRIPTS_DIR = os.path.join(NEOPO_DEPS, "scripts")

raspberry_pi_gcc_arm = "https://github.com/nrobinson2000/neopo/releases/download/0.0.1/gcc-arm-v5.3.1-raspberry-pi.tar.gz"
running_on_windows = platform.system() == "Windows"

particle_cli = os.path.join(NEOPO_DEPS, "particle")

if running_on_windows:
    particle_cli = os.path.join(NEOPO_DEPS, "particle.exe")

jsonFiles = {
    "firmware": os.path.join(CACHE_DIR, "firmware.json"),
    "toolchains": os.path.join(CACHE_DIR, "toolchains.json"),
    "platforms": os.path.join(CACHE_DIR, "platforms.json"),
    "manifest": os.path.join(CACHE_DIR, "manifest.json")
}

vscodeFiles = {
    "dir": os.path.join(NEOPO_DEPS, "vscode"),
    "launch": os.path.join(NEOPO_DEPS, "vscode", "launch.json"),
    "settings": os.path.join(NEOPO_DEPS, "vscode", "settings.json")
}

extensionFiles = {
    "bin": "extension/src/cli/bin",
    "manifest": "extension/src/compiler/manifest.json",
    "launch": "extension/src/cli/vscode/launch.json",
    "settings": "extension/src/cli/vscode/settings.json"
}

projectFiles = {
    "launch": os.path.join(".vscode", "launch.json"),
    "settings": os.path.join(".vscode", "settings.json"),
    "properties": "project.properties"
}

# Load settings from the JSON file
def loadManifest(tupleOrDict):
    with open(jsonFiles["manifest"], "r") as file:
        data = json.load(file)
        if tupleOrDict:
            return (
                data["gcc-arm"],
                data["buildscripts"],
                data["buildtools"],
                data["deviceOS"],
            )
        else:
            return {
                "gcc-arm": data["gcc-arm"],
                "buildscripts": data["buildscripts"],
                "buildtools": data["buildtools"],
                "deviceOS": data["deviceOS"],
                "openocd": data["openocd"],
            }

# Get a deviceOS dependency from a version
def getFirmwareData(version):
    with open(jsonFiles["firmware"], "r") as firmwareFile:
        data = json.load(firmwareFile)
        for entry in data:
            if entry["version"] == version:
                return entry
        return False

# Create the path string for a given deviceOS version
def getFirmwarePath(version):
    deviceOSPath = os.path.join(PARTICLE_DEPS, "deviceOS", version)
    legacy = "firmware-" + version
    github = "device-os-" + version

    if os.path.isdir(os.path.join(deviceOSPath, legacy)):
        deviceOSPath = os.path.join(deviceOSPath, legacy)

    if os.path.isdir(os.path.join(deviceOSPath, github)):
        deviceOSPath = os.path.join(deviceOSPath, github)

    return deviceOSPath

# Add a path to an environment
def addToPath(environment, path):
    if running_on_windows:
        environment["PATH"] = path + ";" + environment["PATH"]
    else:
        environment["PATH"] += ":" + path

# Print available versions compressed (for completion)
def versions_compressed(args):
    with open(jsonFiles["firmware"], "r") as firmwareFile:
        data = json.load(firmwareFile)
        output = ""
        for entry in data:
            output += entry["version"] + " "
        print(output)

# Print available platforms (for completion)
def platforms_command(args):
    with open(jsonFiles["platforms"], "r") as platformFile:
        data = json.load(platformFile)
        output = ""
        for entry in data:
            output += entry["name"] + " "
        print(output)

# Find all valid projects in PWD (for completion)
def findValidProjects(args):
    (_, dirs, _) = next(os.walk(os.getcwd()))
    output = ""
    for dir in dirs:
        if os.access(os.path.join(dir, "project.properties"), os.R_OK):
            output += dir + " "
    print(output)

# Find all makefile targets (for completion)
def getMakefileTargets(args):
    with open(jsonFiles["manifest"], "r") as manifest:
        data = json.load(manifest)
        with open(
                os.path.join(PARTICLE_DEPS, "buildscripts", data["buildscripts"],
                             "Makefile")) as makefile:
            contents = makefile.readlines()
            sep = ".PHONY: "
            for line in contents:
                if line.startswith(sep):
                    print(line.partition(sep)[2].strip("\n"))
                    return


# List all scripts installed (for completion)
def listScripts(args):
    (_, _, files) = next(os.walk(SCRIPTS_DIR))
    print(*files, sep=" ")

# Print all iterable options (for completion)
def iterate_options(args):
    print(*iterable_commands.keys(), sep=" ")

# Available options for iterate
iterable_commands = {
    "compile": command.compile_command,
    "build": command.compile_command,
    "flash": command.flash_command,
    "flash-all": command.flash_all_command,
    "clean": command.clean_command,
    "run": command.run_command,
    "script": script.script
}

# Print all commands (for completion)
def options(args):
    print(*commands.keys(), sep=" ")

# Available options
commands = {
    "help": command.print_help,
    "install": command.install_command,
    "uninstall": install.uninstall,
    "versions": build.versions,
    "create": command.create_command,
    "compile": command.compile_command,
    "build": command.compile_command,
    "flash": command.flash_command,
    "flash-all": command.flash_all_command,
    "clean": command.clean_command,
    "run": command.run_command,
    "configure": command.configure_command,
    "update": command.update_command,
    "get": command.get_command,
    "list-versions": versions_compressed,
    "platforms": platforms_command,
    "projects": findValidProjects,
    "targets": getMakefileTargets,
    "options": options,
    "download-unlisted": command.downloadUnlisted_command,
    "script": script.script,
    "list-scripts": listScripts,
    "load": script.load,
    "iterate": command.iterate_command,
    "options-iterable": iterate_options
}