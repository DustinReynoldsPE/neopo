# Provides access to using neopo as a module:
# import neopo

# # General options
# from .neopo import help, install, upgrade, uninstall, versions, create, particle

# # Build options
# from .neopo import build, flash, flash_all, clean

# # Special options
# from .neopo import run, configure, flags, settings, libs, iterate

# # Script options
# from .neopo import script, script_print, script_wait

# # Dependency options
# from .neopo import update, get

import os


from .utility import print_help, responsible, unexpectedError
from .workbench import installOrUpdate
from .toolchain import versions_command, get_command, downloadUnlisted_command
from .project import create_command, configure_command, flags_command, settings_command, libraries_command
from .build import compile_command, flash_command, flash_all_command, clean_command, run_command
from .completion import versions_compressed, platforms_command, findValidProjects, getMakefileTargets

from .iterate import iterate_command, iterate_options
from .particle import particle_command

from .script import script_command

from .command import commands, upgrade_command, uninstall_command



# Main API for using neopo as a module
def exec(args):
    if isinstance(args, str):
        args = args.split()
    try:
        # Add dummy first argument
        args = ["", *args]
        commands[args[1]](args)
    except IndexError:
        print("Expected a command!")
    except RuntimeError as e:
        print(e)

### General options

def help():
    print_help(None)

def install(force = False):
    installOrUpdate(True, force)

def upgrade():
    upgrade_command(None)

def uninstall():
    uninstall_command(None)

def versions():
    versions_command(None)

def create(projectPath = os.getcwd()):
    create_command([None, None, projectPath])

def particle(args = []):
    if isinstance(args, str):
        args = args.split()
    particle_command([None, None, *args])

### Build options

def build(projectPath = os.getcwd(), verbosity = ""):
    compile_command([None, None, projectPath, verbosity])

def flash(projectPath = os.getcwd(), verbosity = ""):
    flash_command([None, None, projectPath, verbosity])

def flash_all(projectPath = os.getcwd(), verbosity = ""):
    flash_all_command([None, None, projectPath, verbosity])

def clean(projectPath = os.getcwd(), verbosity = ""):
    clean_command([None, None, projectPath, verbosity])

### Special options

def run(target, projectPath = os.getcwd(), verbosity = ""):
    run_command([None, None, target, projectPath, verbosity])

def configure(platform, version, projectPath = os.getcwd()):
    configure_command([None, None, platform, version, projectPath])

def flags(flagsStr, projectPath = os.getcwd()):
    flags_command([None, None, flagsStr, projectPath])

def settings(projectPath = os.getcwd()):
    settings_command([None, None, projectPath])

def libs(projectPath = os.getcwd()):
    libraries_command([None, None, projectPath])

def iterate(args, verbosity = ""):
    iterate_command([None, None, *args, verbosity])

### Script options

def script(scriptName):
    script_command([None, None, scriptName])

### Dependency options

def update():
    installOrUpdate(False, False)

def get(version):
    get_command([None, None, version])