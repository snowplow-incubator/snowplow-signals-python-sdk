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
PROJECT_ROOT=$(realpath "$SCRIPTS_DIR/../..")
API_PORT=8087
# Define the customer repo path
CUSTOMER_REPO_NAME="customer_repo"
CUSTOMER_ROOT_PATH="$PROJECT_ROOT/test/auto_gen"
CUSTOMER_REPO_DIR="$CUSTOMER_ROOT_PATH/$CUSTOMER_REPO_NAME"
API_URL="http://localhost:$API_PORT"

# First, ensure the SDK is properly installed in development mode
print_header() {
    echo -e "\n${YELLOW}======================================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}======================================================${NC}"
}

print_header "Installing the SDK in development mode"
cd "$PROJECT_ROOT"
pip install -e .
echo -e "${GREEN}SDK installed in development mode${NC}"

# Function to clean up on exit
cleanup() {
    echo -e "${BLUE}Returning to original directory: ${ORIGINAL_DIR}${NC}"
    cd "$ORIGINAL_DIR"
    
    # Kill background processes if they exist
    if [ ! -z "$API_PID" ]; then
        echo -e "${BLUE}Shutting down API server with PID: ${API_PID}${NC}"
        kill $API_PID 2>/dev/null || true
    fi
}

# Set trap to ensure we return to the original directory and clean up processes
trap cleanup EXIT INT TERM

# Main execution starts here
print_header "STARTING TEST ENVIRONMENT INITIALIZATION"
echo "$(date)"

# 1. Try to start the API server
print_header "Starting API server"
API_SCRIPT="$CUSTOMER_ROOT_PATH/local_testing/api_server.py"
if [ -f "$API_SCRIPT" ]; then
    python3 "$API_SCRIPT" &
    API_PID=$!
    echo -e "${GREEN}API server started with PID: ${API_PID}${NC}"
    sleep 2
else
    echo -e "${YELLOW}API script not found at $API_SCRIPT - continuing without API server${NC}"
fi

# 2. Set up the mock customer repo
print_header "Setting up mock customer repository"

# Clean up any existing customer repo
if [ -d "$CUSTOMER_REPO_DIR" ]; then
    echo -e "${BLUE}Removing existing customer repository at $CUSTOMER_REPO_DIR${NC}"
    rm -rf "$CUSTOMER_REPO_DIR"
fi

# Create directory if it doesn't exist
mkdir -p "$CUSTOMER_REPO_DIR"
echo -e "${GREEN}Created customer repository at $CUSTOMER_REPO_DIR${NC}"

# 3. Initialize the dbt project using the SDK
print_header "Initializing dbt project with the SDK"
echo -e "${BLUE}Initializing dbt project at $CUSTOMER_REPO_DIR${NC}"

# Verify SDK import and use it
python3 -c "
from snowplow_signals import Signals
print('Successfully imported Signals from snowplow_signals')
client = Signals('$API_URL').dbt
# Use the API to fetch signals config
client.init_project('$CUSTOMER_REPO_DIR')
"
echo -e "${GREEN}Successfully initialized dbt project${NC}"

# 4. Generate the dbt models
print_header "Generating dbt models"
echo -e "${BLUE}Generating dbt models at $CUSTOMER_REPO_DIR${NC}"
python3 -c "
from snowplow_signals import Signals
client = Signals('$API_URL').dbt
# Use the API to fetch signals config
client.generate_models('$CUSTOMER_REPO_DIR', update=True)
"
echo -e "${GREEN}Successfully generated dbt models${NC}"

# 5. Find and run dbt models for all projects
print_header "Running dbt models"

# Check if the customer repo directory exists
if [ ! -d "$CUSTOMER_REPO_DIR" ]; then
    echo -e "${RED}Customer repository not found at $CUSTOMER_REPO_DIR${NC}"
    exit 1
fi

# Change to the customer repo directory
cd "$CUSTOMER_REPO_DIR"

# Check if we have any projects
PROJECTS=$(find . -maxdepth 1 -type d -not -path "." | sed 's|^\./||')
# print PROJECTS
echo -e "${BLUE}Projects: $PROJECTS${NC}"

if [ -z "$PROJECTS" ]; then
    # No separate projects, treat the entire directory as a single project
    echo -e "${BLUE}Using entire customer repository as a single project${NC}"
    
    # Clean up any previous dbt artifacts
    dbt clean
    
    # Run dbt deps and dbt run
    dbt deps
    dbt run --target snowflake --full-refresh
else
    # Process each project
    for PROJECT in $PROJECTS; do
        if [ -d "$PROJECT" ]; then
            print_header "Processing project: $PROJECT"
            cd "$CUSTOMER_REPO_DIR/$PROJECT"
            
            # Check if this is a dbt project
            if [ -f "dbt_project.yml" ]; then
                echo -e "${BLUE}Running dbt commands for project: $PROJECT${NC}"
                
                # Clean up any previous dbt artifacts
                dbt clean
                
                # Run dbt deps and dbt run
                dbt deps

                echo -e "${BLUE}Running dbt initial run for project: $PROJECT${NC}"
                dbt run --target snowflake --full-refresh

                echo -e "${BLUE}Running dbt incremental run 1/3 for project: $PROJECT${NC}"
                dbt run --target snowflake

                echo -e "${BLUE}Running dbt incremental run 2/3 for project: $PROJECT${NC}"
                dbt run --target snowflake

                echo -e "${BLUE}Running dbt incremental run 3/3 for project: $PROJECT${NC}"
                dbt run --target snowflake
            else
                echo -e "${YELLOW}Skipping $PROJECT - not a dbt project (no dbt_project.yml found)${NC}"
            fi
        fi
    done
fi

print_header "TEST ENVIRONMENT INITIALIZATION COMPLETE"
echo "$(date)"
echo -e "\n${GREEN}All initialization steps completed.${NC}"
