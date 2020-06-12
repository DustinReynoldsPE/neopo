import cache
import subprocess
import os
import json
import shutil
import install
import pathlib


# Create a Particle project and copy in Workbench settings
def create(path, name):
    tempEnv = os.environ.copy()
    cache.addToPath(tempEnv, cache.NEOPO_DEPS)

    returncode = subprocess.run(
        ["particle", "project", "create", path, "--name", name],
        env=tempEnv,
        shell=cache.running_on_windows).returncode
    if returncode:
        exit(returncode)

    #TODO: Default device in manifest.json
    device = "argon"
    version = cache.loadManifest(True)[-1]
    configure(os.path.join(path, name), device, version)


# Convert between platform IDs and device names
def platformConvert(data, key1, key2):
    with open(cache.jsonFiles["platforms"], "r") as platformFile:
        platforms = json.load(platformFile)
        for platform in platforms:
            if platform[key1] == data:
                return platform[key2]
        return False

# List the supported platform IDs for a given version
def getSupportedPlatforms(version):
    with open(cache.jsonFiles["toolchains"], "r") as toolchainsFile:
        toolchains = json.load(toolchainsFile)
        for toolchain in toolchains:
            if toolchain["firmware"] == "deviceOS@" + version:
                return toolchain["platforms"]
        return False

# Verify platform and deviceOS version and download deviceOS dependency if required
def checkFirmwareVersion(platform, version):
    firmware = cache.getFirmwareData(version)
    platformID = platformConvert(platform, "name", "id")

    if not platformID:
        print("Invalid platform", platform + "!")
        return False

    if not firmware:
        print("Invalid deviceOS version", version + "!")
        return False

    if not platformID in getSupportedPlatforms(version):
        print("Platform", platform, " is not supported in deviceOS version",
              version + "!")
        return False

    path = os.path.join(cache.PARTICLE_DEPS, "deviceOS", version)
    if os.path.isdir(path):
        return True

    install.downloadDep(firmware, False)
    return True

# Modify Workbench settings in a project (platform, firmwareVersion)
def configure(projectPath, platform, firmwareVersion):
    if not checkFirmwareVersion(platform, firmwareVersion):
        exit(1)

    if not os.path.isfile(os.path.join(projectPath, cache.projectFiles["settings"])):
        pathlib.Path(os.path.join(projectPath, ".vscode")).mkdir(parents=True,
                                                                 exist_ok=True)
        shutil.copyfile(cache.vscodeFiles["launch"],
                        os.path.join(projectPath, cache.projectFiles["launch"]))
        shutil.copyfile(cache.vscodeFiles["settings"],
                        os.path.join(projectPath, cache.projectFiles["settings"]))

    writeSettings(projectPath, platform, firmwareVersion)
    print("Configured project", projectPath + ":")
    print("\tparticle.targetPlatform:", platform)
    print("\tparticle.firmwareVersion:", firmwareVersion)


# Load Workbench settings from a project
def getSettings(projectPath):
    with open(os.path.join(projectPath, cache.projectFiles["settings"]),
              "r+") as settings:
        data = json.loads(settings.read())
        return (data["particle.targetPlatform"],
                data["particle.firmwareVersion"])

# Update Workbench settings in a project
def writeSettings(projectPath, platform, version):
    with open(os.path.join(projectPath, cache.projectFiles["settings"]),
              "r+") as settings:
        data = json.loads(settings.read())
        data["particle.targetPlatform"] = platform
        data["particle.firmwareVersion"] = version
        settings.seek(0)
        json.dump(data, settings, indent=4)
        settings.truncate()


# Use the Makefile to build the specified target
def build(projectPath, command, helpOnly, verbosity):
    compilerVersion, scriptVersion, toolsVersion, firmwareVersion = cache.loadManifest(
        True)
    tempEnv = os.environ.copy()
    cache.addToPath(tempEnv, os.path.join(cache.PARTICLE_DEPS, "gcc-arm", compilerVersion, "bin"))

    particle = cache.particle_cli

    if cache.running_on_windows:
        cache.addToPath(tempEnv, os.path.join(cache.PARTICLE_DEPS, "buildtools", toolsVersion,
                                        "bin"))
        particle = particle.replace("C:\\", "/cygdrive/c/")
        particle = particle.replace("\\", "/")
    else:
        cache.addToPath(tempEnv, os.path.join(cache.PARTICLE_DEPS, "buildtools", toolsVersion))

    process = [
        "make", "-sf",
        os.path.join(cache.PARTICLE_DEPS, "buildscripts", scriptVersion, "Makefile"),
        "PARTICLE_CLI_PATH=" + particle
    ]

    # Remove [s] flag from make to get verbose output
    if verbosity == 1:
        process[1] = "-f"

    if helpOnly:
        process.append("help")
    else:
        try:
            devicePlatform, firmwareVersion = getSettings(projectPath)
        except FileNotFoundError:
            if os.path.isfile(
                    os.path.join(projectPath, cache.projectFiles['properties'])):
                print("Project not configured!")
                print("Use: neopo configure <platform> <version> <project>")
                return
            else:
                raise

        if cache.running_on_windows:
            projectPath = projectPath.replace("\\", "\\\\")

        deviceOSPath = cache.getFirmwarePath(firmwareVersion)
        process.append("APPDIR=" + projectPath)
        process.append("DEVICE_OS_PATH=" + deviceOSPath)
        process.append("PLATFORM=" + devicePlatform)
        process.append(command)

    returncode = subprocess.run(process, env=tempEnv,
                                shell=cache.running_on_windows,
                                stdout= subprocess.PIPE if verbosity == -1 else None,
                                stderr= subprocess.PIPE if verbosity == -1 else None
                                ).returncode
    if returncode:
        exit(returncode)

# Print available versions and platforms
def versions(args):
    with open(cache.jsonFiles["firmware"], "r") as firmwareFile:
        data = json.load(firmwareFile)
        print("Available deviceOS versions:")
        print()
        data.reverse()
        for entry in data:
            version = entry["version"]
            platforms = getSupportedPlatforms(version)
            devices = []
            for platform in platforms:
                devices.append(platformConvert(platform, "id", "name"))

            devicesStr = devices[0]
            for device in devices[1:]:
                devicesStr += ", " + device

            print("  ", version + "\t", "[", devicesStr, "]")

        print()
        print("To configure a project use:")
        print("\tneopo configure <platform> <version> <project>")