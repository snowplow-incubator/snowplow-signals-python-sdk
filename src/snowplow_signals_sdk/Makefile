# Define variables
DBT_REPO = git@github.com:snowplow-incubator/snowplow-dbt-autogen.git
DBT_DIR = dbt_project
FEATURE_JSON_DIR =  scripts
UTILS_DIR = $(DBT_DIR)/utils
CONFIG_FILE = $(UTILS_DIR)/config.json

# Clone/update dbt project template
initialize:
	@if [ ! -d "$(DBT_DIR)/.git" ]; then \
		git clone --branch develop $(DBT_REPO) $(DBT_DIR); \
	else \
		cd $(DBT_DIR) && git pull; \
	fi
	git clone $(DBT_REPO) $(DBT_DIR) || (cd $(DBT_DIR) && git pull)
	mkdir -p $(UTILS_DIR)
	mkdir -p $(DBT_DIR)/models/features
	
# TODO:Fetch latest feature definitions from the API (faked it for now with dummy JSON)
# fetch-features:
# 	python3 -m scripts.fetch_features

generate-config-overview:
	python3 -m scripts.generate_config_overview

# Autogenerate dbt models
generate-models:
	python3 -m scripts.generate_dbt_models

# Cleanup step (optional)
clean:
	rm -rf $(DBT_DIR)

# Set up and autogenerate at once
all: initialize generate-config-overview generate-models


