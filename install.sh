#!/bin/bash

# neopo: A lightweight solution for local Particle development.
# Copyright (c) 2020 Nathan Robinson.

case "$(uname)" in Linux)
echo "You may need to install the following dependencies:"
echo -e "\tlibarchive-zip-perl libc6-i386"
echo -e "\tsudo apt install libarchive-zip-perl libc6-i386" ;;
Darwin) ;;
*) >&2 echo "Your OS is not supported! Use Linux or macOS." ; exit 1
esac

echo "Downloading installation script..."
curl -LO "https://raw.githubusercontent.com/nrobinson2000/neopo/master/bin/install.py"
python3 install.py && neopo install
rm install.py

if [ "$(uname)" == "Linux" ]; then
echo "Installing tab completion script:"
sudo curl -fsSLo /etc/bash_completion.d/neopo "https://raw.githubusercontent.com/nrobinson2000/neopo/master/bin/neopo-completion"
else
echo "The tab completion script is recommended for the best experience:"
echo "You can download it from:"
echo "  https://raw.githubusercontent.com/nrobinson2000/neopo/master/bin/neopo-completion"
echo "To load it you would run:"
echo "  $ source neopo-completion"
fi