#!/bin/bash

if [[ "$EUID" == 0 ]]; then
    echo 'Do not run as root!' 1>&2;

    exit 1
fi

mkdir -p ~/.neopo/bin
mkdir -p ~/.neopo/etc
mkdir -p ~/.neopo/src
mkdir -p ~/.neopo/cache
mkdir -p ~/.neopo/share

directory="$(mktemp -d)"

#trap "rm -rf '$directory'" 0 2 3 15

git clone https://github.com/nrobinson2000/neopo.git "$directory"
git -C "$directory" checkout dev

mv "$directory/dist/unix/bin" ~/.neopo
mv "$directory/dist/unix/etc" ~/.neopo
mv "$directory/src" ~/.neopo

if [[ "$(uname)" == 'Linux' ]] && hash apt > /dev/null 2>&1; then
    echo 'Installing apt dependencies...'

    case "$(uname -m)" in
        x86_64)
            sudo apt install libarchive-zip-perl libc6-i386;;

        armv7l)
            sudo apt install libarchive-zip-perl libusb-1.0-0-dev dfu-util libudev-dev;;
    esac
fi

case "$SHELL" in
    /bin/bash)
        echo 'export PATH="$HOME/.neopo/bin:$PATH"' >> ~/.bashrc
        echo 'source "$HOME/.neopo/etc/bash_completion.d/neopo.sh"' >> ~/.bashrc;;

    /bin/zsh)
        echo 'export PATH="$HOME/.neopo/bin:$PATH"' >> ~/.zprofile
        echo 'source "$HOME/.neopo/etc/bash_completion.d/neopo.sh"' >> ~/.zprofile;;

    *)
        echo 'Warning: You are not running bash or zsh so neopo cannot be added to your PATH automatically.'

        echo 'Add this to your PATH: ~/.neopo/bin'
        echo 'Source this on startup for completion: ~/.neopo/etc/bash_completion.d/neopo';;
esac

~/.neopo/bin/neopo install
