import argparse
import json
import logging
import os
import sys

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def fetch_attributes(api_url=None, source_type="offline", output_path=None):
    """
    Fetch attribute views from the API and save them for processing.

    Args:
        api_url (str): The base URL of the API server
        source_type (str): Type of source to fetch (online or offline)
        output_path (str): Path to save the fetched attributes JSON

    Returns:
        list: The fetched attribute views
    """
    # Default API URL if not provided
    if api_url is None:
        api_url = "http://localhost:8087"

    # If full URL provided, take it as is
    if "api/v1/registry/views" in api_url:
        full_url = api_url
    # Construct the full URL with query parameters TODO: this needs fixing
    else:
        full_url = f"{api_url}/api/v1/registry/views?source_type={source_type}"
    logger.info(f"Fetching attributes from the API")
    try:
        logger.debug(f"API URL: {full_url}")
        response = requests.get(full_url)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        # Parse the response
        attributes_data = response.json()
        logger.debug(f"Received API response: {json.dumps(attributes_data, indent=2)}")

        if not attributes_data:
            logger.warning("No no attributes found in API response. Exiting.")
            sys.exit(1)

        # If output_path provided, save the response
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(attributes_data, f, indent=4)
            logger.info(f"API response saved to {output_path}")

        # Normalize data format
        # Ensure we have a list of attribute arrays
        if not isinstance(attributes_data, list):
            logger.debug("API returned non-list, wrapping in list")
            attributes_data = [attributes_data]

        # Validate expected structure
        for item in attributes_data:
            if not isinstance(item, dict):
                raise ValueError(f"Expected dict items in response, got {type(item)}")

            if "attributes" not in item:
                raise ValueError("Response items missing required 'attributes' key")

        return attributes_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching attributes: {e}")
        logger.info("Using static signals config as fallback")

        try:
            # Load static signals config
            script_dir = os.path.dirname(os.path.abspath(__file__))
            static_config_path = os.path.join(
                script_dir,
                "..",
                "..",
                "..",
                "integration_tests",
                "local_testing",
                "static_signals_config_offline.json",
            )

            with open(static_config_path) as f:
                attributes_data = json.load(f)

            # If output_path provided, save the fallback data
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    json.dump(attributes_data, f, indent=4)
                logger.info(f"Fallback config saved to {output_path}")

            logger.info("Successfully loaded static signals config")
            return attributes_data

        except Exception as fallback_error:
            logger.error(f"Error loading static signals config: {fallback_error}")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch attribute views from API")
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8087",
        help="Base URL of the API server",
    )
    parser.add_argument("--output", type=str, help="Path to save the fetched attributes JSON")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    fetch_attributes(api_url=args.api_url, output_path=args.output)
