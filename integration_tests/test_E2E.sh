#!/bin/bash
# =============================================================================
# Test Environment Initialization Script using SDK's dbt functionality
# =============================================================================

# Parse --target argument
while getopts 'd:' opt
do
  case $opt in
    d) DATABASE=$OPTARG
  esac
done



# Basic error handling
set -e

# Define color codes for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Store the original directory
ORIGINAL_DIR=$(pwd)
SCRIPTS_DIR=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(dirname "$SCRIPTS_DIR")


# Validate DATABASE variable
if [ -z "$DATABASE" ]; then
  echo "ERROR: DATABASE environment variable is not set."
  exit 1
fi

NEW_TEST_DIR="${PROJECT_ROOT}/integration_tests/customer_repo_${DATABASE}/ecommerce_transaction_interactions_features_1/integration_test"


print_header() {
    echo -e "\n${YELLOW}======================================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}======================================================${NC}"
}

print_header "Installing the SDK in development mode"
cd "$PROJECT_ROOT"
echo -e "${GREEN}SDK installed in development mode${NC}"

# Main execution starts here
print_header "STARTING TEST ENVIRONMENT INITIALIZATION"
echo "$(date)"

# Run the test script with pytest to generate the dbt project
print_header "Running replicate_files.py"
poetry run python integration_tests/replicate_files.py test/auto_gen/__snapshots__/test_snapshots_$DATABASE.ambr integration_tests/customer_repo_$DATABASE

# Check if test_dir was created successfully
if [ ! -d "integration_tests/customer_repo_${DATABASE}" ]; then
    echo -e "${RED}Failed to create integration_tests/customer_repo_${DATABASE}${NC}"
    exit 1
fi

echo -e "${GREEN}Successfully initialized and generated dbt project for ${DATABASE}${NC}"


# Create the destination directory
mkdir -p "$(dirname "$NEW_TEST_DIR")"

# Move the integration_test directory
mv "${PROJECT_ROOT}/integration_tests/integration_test" "$NEW_TEST_DIR"

# Move into the new test directory
cd "$NEW_TEST_DIR"

# Print header
print_header "Running dbt commands"

# Run dbt dependencies
echo -e "${BLUE}Installing dbt dependencies...${NC}"
dbt deps

# Run integration test script
bash .scripts/integration_test.sh -d "$DATABASE"


print_header "E2E TEST COMPLETED"
echo "$(date)"
echo -e "\n${GREEN}All E2E test steps completed.${NC}"
