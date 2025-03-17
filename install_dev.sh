#!/bin/bash
# Script to install MUXI packages in development mode

echo "Installing MUXI packages in development mode..."

# Install core package first
echo "Installing muxi-core..."
pip install -e packages/core

# Install server package
echo "Installing muxi-server..."
pip install -e packages/server

# Install CLI package
echo "Installing muxi-cli..."
pip install -e packages/cli

# Install meta-package (core + server + cli)
echo "Installing muxi (meta-package)..."
pip install -e packages/muxi

# Install web package separately
echo "Installing muxi-web..."
pip install -e packages/web

echo "Done!"
echo ""
echo "You can now use MUXI in development mode:"
echo "- Full system: 'import muxi'"
echo "- Web client only: 'import muxi.web'"
echo "- CLI client only: Use the 'muxi' command"
