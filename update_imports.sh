#!/bin/bash
# Script to update import references from src to muxi

echo "Updating import references from 'src.' to 'muxi.'..."
find packages -name "*.py" -type f -exec sed -i '' 's/from src\./from muxi./g' {} \;
find packages -name "*.py" -type f -exec sed -i '' 's/import src\./import muxi./g' {} \;

echo "Done!"
