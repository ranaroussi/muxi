#!/bin/bash

# Run version tests

echo "Running AI Agent Framework version tests..."
echo "============================================="

# Change to the project root directory
cd "$(dirname "$0")"

# Run the tests
python -m tests.run_version_tests

# Get the exit code
EXIT_CODE=$?

# Print result based on exit code
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n✅ All version tests passed!"
else
    echo -e "\n❌ Some version tests failed!"
fi

# Exit with the same code as the Python script
exit $EXIT_CODE
