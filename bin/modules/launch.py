#!/usr/bin/env python3

import sys
import command
import cache

# Evaluate command-line arguments and call necessary functions
def main():
    if len(sys.argv) == 1:
        command.print_help(sys.argv)
    elif sys.argv[1] in cache.commands:
        cache.commands[sys.argv[1]](sys.argv)
    else:
        print("Invalid command!")
        command.print_help(sys.argv)

if __name__ == "__main__":
    # print(sys.argv)
    main()
