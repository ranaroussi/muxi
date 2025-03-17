#!/bin/bash
# Script to clean up the old src directory after successful migration

echo "WARNING: This script will delete the old src directory."
echo "Make sure you have successfully migrated all code to the new packages structure."
echo "Make sure you have committed your changes to git before proceeding."
echo ""
read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing old src directory..."
    rm -rf src
    echo "Done!"
else
    echo "Operation cancelled."
fi
