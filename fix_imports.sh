#!/bin/bash
# =====================================================================
# MUXI Import Fixer Script
# =====================================================================
# This script updates import references to align with the new package
# structure and creates necessary symlinks for development mode.
#
# When to use:
# - After pulling in changes that modify import paths
# - When you experience import errors with cross-package references
# - After adding new modules that import across package boundaries
#
# What it does:
# 1. Fixes imports in core to reference server components
# 2. Fixes internal imports in the server package
# 3. Creates symlinks for cross-package dependencies
#
# NOTE: This script is for development only. In production, these
# imports will be resolved through proper package dependencies.
# =====================================================================

echo "Fixing imports for core package..."
# Move config from core to server
find packages/core -name "*.py" -type f -exec sed -i '' 's/from muxi.config/from muxi.server.config/g' {} \;
find packages/core -name "*.py" -type f -exec sed -i '' 's/import muxi.config/import muxi.server.config/g' {} \;

# Move memory from core to server
find packages/core -name "*.py" -type f -exec sed -i '' 's/from muxi.memory/from muxi.server.memory/g' {} \;
find packages/core -name "*.py" -type f -exec sed -i '' 's/import muxi.memory/import muxi.server.memory/g' {} \;

# Move tools from core to server
find packages/core -name "*.py" -type f -exec sed -i '' 's/from muxi.tools/from muxi.server.tools/g' {} \;
find packages/core -name "*.py" -type f -exec sed -i '' 's/import muxi.tools/import muxi.server.tools/g' {} \;

echo "Fixing imports for server package..."
# Fix internal imports in server package
find packages/server -name "*.py" -type f -exec sed -i '' 's/from muxi.config/from muxi.server.config/g' {} \;
find packages/server -name "*.py" -type f -exec sed -i '' 's/import muxi.config/import muxi.server.config/g' {} \;

find packages/server -name "*.py" -type f -exec sed -i '' 's/from muxi.memory/from muxi.server.memory/g' {} \;
find packages/server -name "*.py" -type f -exec sed -i '' 's/import muxi.memory/import muxi.server.memory/g' {} \;

find packages/server -name "*.py" -type f -exec sed -i '' 's/from muxi.tools/from muxi.server.tools/g' {} \;
find packages/server -name "*.py" -type f -exec sed -i '' 's/import muxi.tools/import muxi.server.tools/g' {} \;

find packages/server -name "*.py" -type f -exec sed -i '' 's/from muxi.api/from muxi.server.api/g' {} \;
find packages/server -name "*.py" -type f -exec sed -i '' 's/import muxi.api/import muxi.server.api/g' {} \;

echo "Creating symlinks for cross-package dependencies..."
# Instead of updating all imports, let's create symlinks for now for development mode
mkdir -p packages/core/src/muxi/server
ln -sf "$(pwd)/packages/server/src/muxi/config" packages/core/src/muxi/server/config
ln -sf "$(pwd)/packages/server/src/muxi/memory" packages/core/src/muxi/server/memory
ln -sf "$(pwd)/packages/server/src/muxi/tools" packages/core/src/muxi/server/tools

# Fix imports in the config module itself
find packages/server/src/muxi/config -name "*.py" -type f -exec sed -i '' 's/from muxi.config/from muxi.server.config/g' {} \;
find packages/server/src/muxi/memory -name "*.py" -type f -exec sed -i '' 's/from muxi.memory/from muxi.server.memory/g' {} \;
find packages/server/src/muxi/tools -name "*.py" -type f -exec sed -i '' 's/from muxi.tools/from muxi.server.tools/g' {} \;
find packages/server/src/muxi/api -name "*.py" -type f -exec sed -i '' 's/from muxi.api/from muxi.server.api/g' {} \;

echo "Import fixing complete!"
echo ""
echo "To verify your changes, try running: python -c \"from muxi import muxi; print('Imports working!')\""
