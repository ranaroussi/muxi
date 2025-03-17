#!/bin/bash
# =====================================================================
# MUXI Old Structure Cleanup Script
# =====================================================================
# This script removes the old src/ directory after successful migration
# to the new packages structure.
#
# IMPORTANT: Only run this after you have:
# 1. Successfully migrated all code to the new packages structure
# 2. Tested that the new structure works correctly
# 3. Committed your changes to git
#
# This is a destructive operation and cannot be undone!
# =====================================================================

echo "WARNING: This script will delete the old src directory."
echo "Make sure you have successfully migrated all code to the new packages structure."
echo "Make sure you have committed your changes to git before proceeding."
echo ""
read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing old src directory..."
    rm -rf src
    echo "Done! The old src/ directory has been removed."
    echo ""
    echo "Next steps:"
    echo "1. Commit this change: git commit -m \"Remove old src directory after migration\""
    echo "2. Update your documentation to reflect the new structure"
else
    echo "Operation cancelled."
fi
