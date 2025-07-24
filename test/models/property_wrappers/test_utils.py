from snowplow_signals.models.property_wrappers.utils import (
    _clean_name,
    _clean_vendor,
    _clean_version,
)


class TestUtilityFunctions:
    """Test the utility functions for cleaning vendor, name, and version strings."""

    def test_clean_vendor(self):
        """Test vendor string cleaning functionality."""
        assert (
            _clean_vendor("com.snowplowanalytics.snowplow")
            == "com_snowplowanalytics_snowplow"
        )

    def test_clean_name(self):
        """Test name string cleaning functionality."""
        assert _clean_name("snowplow_ecommerce_action") == "snowplow_ecommerce_action"
        assert _clean_name("CamelCase") == "camel_case"
        assert _clean_name("simpleString") == "simple_string"
        assert _clean_name("HTMLParser") == "htmlparser"

    def test_clean_version(self):
        assert _clean_version("1") == "1"
        assert _clean_version(1) == "1"
