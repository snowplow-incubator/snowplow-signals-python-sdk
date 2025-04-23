#!/bin/bash
# =============================================================================
# Test Environment Initialization Script using SDK's dbt functionality
# =============================================================================

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
poetry run python integration_tests/replicate_files.py test/auto_gen/__snapshots__/test_snapshots.ambr local_testing/customer_repo

# Check if test_dir was created successfully
if [ ! -d "local_testing/customer_repo" ]; then
    echo -e "${RED}Failed to create local_testing/customer_repo${NC}"
    exit 1
fi

echo -e "${GREEN}Successfully initialized and generated dbt project${NC}"

# Run dbt commands for each project
print_header "Running dbt commands"

# Find all dbt projects (directories containing dbt_project.yml)
cd local_testing/customer_repo
for project_dir in */; do
    if [ -f "${project_dir}dbt_project.yml" ]; then
        print_header "Processing project: ${project_dir%/}"
        cd "${project_dir}"
        
        # Clean up any previous dbt artifacts
        echo -e "${BLUE}Cleaning dbt artifacts...${NC}"
        dbt clean
        
        # Install dependencies
        echo -e "${BLUE}Installing dbt dependencies...${NC}"
        dbt deps
        
        # Run models with full refresh
        echo -e "${BLUE}Running dbt models with full refresh...${NC}"
        dbt run --target snowflake --full-refresh
        
        # Run models incrementally
        echo -e "${BLUE}Running dbt models incrementally...${NC}"
        dbt run --target snowflake
        
        cd ..
    fi
done

print_header "TEST ENVIRONMENT INITIALIZATION COMPLETE"
echo "$(date)"
echo -e "\n${GREEN}All initialization steps completed.${NC}"
