#!/bin/bash

# Download particle completion
#curl -sLo "~/.completions/particle" "https://raw.githubusercontent.com/nrobinson2000/particle-cli-completion/master/particle"

# Use custom path
export NEOPO_PATH="$HOME/.neopo"
mkdir -p $NEOPO_PATH

# Preinstall neopo and particle
neopo install -s

# Modify dotfiles
cat >> .bashrc << EOF

# neopo settings
export NEOPO_PATH="$NEOPO_PATH"
source ~/.completions/particle
source ~/.completions/neopo
alias vim='vim.tiny'
alias ls='ls --color=auto'
alias ll='ls -la'
alias la='ls -A'
EOF

