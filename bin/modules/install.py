import json
import urllib.request
import os
import pathlib
import platform
import io
import zipfile
import tarfile
import stat
import cache

# Find the Workbench extension URL from the Visual Studio Marketplace
def getExtensionURL():
    print("Finding Workbench extension URL...")
    payload = '{"assetTypes":null,"filters":[{"criteria":[{"filterType":7,"value":"particle.particle-vscode-core"}],"direction":2,"pageSize":100,"pageNumber":1,"sortBy":0,"sortOrder":0,"pagingToken":null}],"flags":103}'

    request = urllib.request.Request(
        "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
        method="POST",
        headers={
            "content-type":
            "application/json",
            "accept":
            "application/json;api-version=6.0-preview.1;excludeUrls=true",
        },
        data=payload.encode("utf-8"),
    )

    with urllib.request.urlopen(request) as response:
        content = response.read()

    data = json.loads(content.decode("utf-8"))
    return data["results"][0]["extensions"][0]["versions"][0]["files"][-1]["source"]

# Download the the Workbench extension from the URL
def getExtension(url):
    print("Downloading Workbench extension...")
    with urllib.request.urlopen(url) as response:
        content = response.read()
    return zipfile.ZipFile(io.BytesIO(content), "r")

# Load a file from a ZIP
def getFile(file, path):
    content = file.read(path)
    return content

# Download the specified dependency
def downloadDep(dep, updateManifest):
    if updateManifest:
        writeManifest(dep)

    name, version, url = dep["name"], dep["version"], dep["url"]
    print("Downloading dependency", name, "version", version + "...")

    with urllib.request.urlopen(url) as response:
        content = response.read()

    path = os.path.join(cache.PARTICLE_DEPS, name, version)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    fileName = os.path.join(path, name + "-v" + version + ".tar.gz")
    with open(fileName, "wb") as gzFile:
        gzFile.write(content)

    with tarfile.open(fileName, "r:gz") as file:
        file.extractall(path)

    os.remove(fileName)

# Write JSON data to a file
def writeFile(content, path):
    with open(path, "wb") as file:
        file.write(content)

# Write an executable dependency to a file
def writeExecutable(content, path):
    with open(path, "wb") as file:
        file.write(content)
        st = os.stat(file.name)
        os.chmod(file.name, st.st_mode | stat.S_IEXEC)

# Download extension manifest and simple dependencies
def getDeps():
    osPlatform = platform.system().lower()    
    osArch = platform.machine().lower() if cache.running_on_windows else "amd64" if platform.machine() == "x86_64" else "arm"

    pathlib.Path(cache.CACHE_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(cache.SCRIPTS_DIR).mkdir(parents=True, exist_ok=True)

    extension = getExtension(getExtensionURL())
    pathlib.Path(cache.vscodeFiles["dir"]).mkdir(parents=True, exist_ok=True)
    manifest = getFile(extension, cache.extensionFiles["manifest"])

    particle_bin = "particle.exe" if cache.running_on_windows else "particle"

    particle = getFile(
        extension, cache.extensionFiles["bin"] + "/" + osPlatform + "/" + osArch +
        "/" + particle_bin)
    launch = getFile(extension, cache.extensionFiles["launch"])
    settings = getFile(extension, cache.extensionFiles["settings"])

    writeFile(launch, cache.vscodeFiles["launch"])
    writeFile(settings, cache.vscodeFiles["settings"])
    writeExecutable(particle, cache.particle_cli)
    createManifest()

    data = json.loads(manifest.decode("utf-8"))
    return data

# Update the manifest JSON file
def writeManifest(dep):
    with open(cache.jsonFiles["manifest"], "r+") as file:
        try:
            manifest = json.load(file)
        except json.decoder.JSONDecodeError:
            manifest = {}

        manifest[dep["name"]] = dep["version"]
        file.seek(0)
        json.dump(manifest, file, indent=4)
        file.truncate()

# Create the manifest file
def createManifest():
    if not os.path.isfile(cache.jsonFiles["manifest"]):
        with open(cache.jsonFiles["manifest"], "w") as file:
            pass

# Write an object to JSON file
def writeJSONcache(data, key):
    with open(cache.jsonFiles[key], "w") as file:
        keyData = data[key]
        json.dump(keyData, file, indent=4)

# Attempt to download deviceOS version not specified in manifest (experimental)
def downloadUnlisted(version):
    firmware = {
        "name": "deviceOS",
        "version": version,
        "url": "https://binaries.particle.io/device-os/v" + version + ".tar.gz"
    }

    print("Trying binaries.particle.io/device-os...")

    try:
        downloadDep(firmware, False)
        return
    except urllib.error.HTTPError:
        print("DeviceOS version", version, "not found!")
        print()

    # Try to download from github
    firmware = {
        "name": "deviceOS",
        "version": version,
        "url": "https://github.com/particle-iot/device-os/archive/v" + version + ".tar.gz"
    }

    print("Trying github.com/particle-iot/device-os...")

    try:
        downloadDep(firmware, False)
        return
    except urllib.error.HTTPError:
        print("DeviceOS version", version, "not found!")

# Download a specific deviceOS version
def downloadFirmware(version):
    firmware = cache.getFirmwareData(version)
    if firmware:
        downloadDep(firmware, False)
    else:
        print("Could not download deviceOS version", version + "!")

# Install or update neopo dependencies (not the neopo script)
def installOrUpdate(install):
    if install:
        print("Installing neopo...")
    else:
        print("Updating dependencies...")

    dependencies = ["compilers", "tools", "scripts", "debuggers"]
    caches = ["firmware", "platforms", "toolchains"]

    data = getDeps()
    depJSON = []
    depJSON.append(data["firmware"][0])

    for dep in dependencies:
        depJSON.append(data[dep][platform.system().lower()]["x64"][0])

    # Support for Raspberry Pi
    if platform.machine() == "armv7l":
        for dep in depJSON:
            if dep["name"] == "gcc-arm":
                dep["url"] = cache.raspberry_pi_gcc_arm
                break

    for key in caches:
        writeJSONcache(data, key)

    if install:
        for dep in depJSON:
            downloadDep(dep, True)
        print("Finished installation. To create a project use:")
        print("\tneopo create <project>")
    else:
        for dep in depJSON:
            manifest = cache.loadManifest(False)
            new = int(dep["version"].split("-")[0].replace(".", ""))
            old = int(manifest[dep["name"]].split("-")[0].replace(".", ""))
            if new > old:
                downloadDep(dep, True)
        print("Dependencies are up to date!")

# Delete the neopo script from the system
def uninstall(args):
    execpath = args[0]
    print("Are you sure you want to uninstall neopo at", execpath + "?")

    answer = input("(Y/N): ")
    if answer.lower() != "y":
        print("Aborted.")
        return

    try:
        os.remove(execpath)
    except PermissionError:
        print("Could not delete", execpath)
        print("Try running with sudo.")
        exit(1)

    print("Uninstalled neopo.")
    print(
        "Note: The .particle directory may still exist (remove it with `rm -rf ~/.particle`)"
    )