#!/bin/bash
# =====================================================================
# MUXI Development Installation Script
# =====================================================================
# This script installs all MUXI packages in development mode,
# allowing you to modify the code without reinstalling.
#
# What it does:
# 1. Installs muxi-core package in editable mode
# 2. Installs muxi-server package in editable mode
# 3. Installs muxi-cli package in editable mode
# 4. Installs muxi metapackage in editable mode
# 5. Installs muxi-web package in editable mode
#
# Installation order matters due to dependencies!
# =====================================================================

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

echo "Development installation complete!"
echo ""
echo "You can now use MUXI in development mode:"
echo "- Full system: 'import muxi'"
echo "- Web client only: 'import muxi.web'"
echo "- CLI client only: Use the 'muxi' command"
echo ""
echo "Next step: Run './fix_imports.sh' to ensure all imports are correctly set up"
