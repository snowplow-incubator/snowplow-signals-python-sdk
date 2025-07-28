import re

import pytest
from jsonpath_ng.exceptions import JsonPathParserError

from snowplow_signals.models.property_wrappers.path_translation import (
    JsonPathTranslator,
)


class TestPathTranslation:
    """Test the PathTranslation utility class."""

    def test_descendant_operator_rejected(self):
        """Test that descendant operators (..) are rejected."""
        jsonpath = "$.events[0]..name"
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Descendant operators (..) are not supported. Please use explicit paths only."
            ),
        ):
            JsonPathTranslator.validate(jsonpath)

    def test_valid_root_only(self):
        """Test that root-only path is valid."""
        jsonpath = "$"
        result = JsonPathTranslator.validate(jsonpath)
        assert result == jsonpath

    def test_valid_simple_field(self):
        """Test that simple field access is valid."""
        jsonpath = "$.name"
        result = JsonPathTranslator.validate(jsonpath)
        assert result == jsonpath

    def test_valid_nested_fields(self):
        """Test that nested field access is valid."""
        jsonpath = "$.user.profile.name"
        result = JsonPathTranslator.validate(jsonpath)
        assert result == jsonpath

    def test_valid_array_index(self):
        """Test that array index access is valid."""
        jsonpath = "$.events[0]"
        result = JsonPathTranslator.validate(jsonpath)
        assert result == jsonpath

    def test_valid_nested_array_index(self):
        """Test that nested array index access is valid."""
        jsonpath = "$.events[0].items[1].name"
        result = JsonPathTranslator.validate(jsonpath)
        assert result == jsonpath

    def test_wildcard_rejected(self):
        """Test that wildcard (*) operators are rejected."""
        jsonpath = "$.events[*].name"
        with pytest.raises(
            ValueError,
            match=re.escape("Unsupported JSONPath, please only use paths and indexes."),
        ):
            JsonPathTranslator.validate(jsonpath)

    def test_slice_operator_rejected(self):
        """Test that slice operators are rejected."""
        jsonpath = "$.events[0:5]"
        with pytest.raises(
            ValueError,
            match=re.escape("Unsupported JSONPath, please only use paths and indexes."),
        ):
            JsonPathTranslator.validate(jsonpath)

    def test_filter_expression_rejected(self):
        """Test that filter expressions are rejected."""
        jsonpath = "$.events[?(@.type == 'click')]"
        with pytest.raises(
            ValueError,
            match=re.escape("Unsupported JSONPath, please only use paths and indexes."),
        ):
            JsonPathTranslator.validate(jsonpath)

    def test_union_operator_rejected(self):
        """Test that union operators are rejected."""
        # Note: This syntax causes a parse error in jsonpath-ng, which is also acceptable
        jsonpath = "$.events[0,1,2]"
        with pytest.raises(
            (ValueError, JsonPathParserError)
        ):  # Can be either ValueError from our validator or parse error
            JsonPathTranslator.validate(jsonpath)

    def test_recursive_descent_with_wildcard_rejected(self):
        """Test that recursive descent with wildcard is rejected."""
        jsonpath = "$..*.name"
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Descendant operators (..) are not supported. Please use explicit paths only."
            ),
        ):
            JsonPathTranslator.validate(jsonpath)

    def test_script_expression_rejected(self):
        """Test that script expressions are rejected."""
        # Note: This syntax causes a parse error in jsonpath-ng, which is also acceptable
        jsonpath = "$.events[(@.length-1)]"
        with pytest.raises(
            (ValueError, JsonPathParserError)
        ):  # Can be either ValueError from our validator or parse error
            JsonPathTranslator.validate(jsonpath)

    def test_multiple_descendant_operators_rejected(self):
        """Test that multiple descendant operators are rejected."""
        jsonpath = "$..events..name"
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Descendant operators (..) are not supported. Please use explicit paths only."
            ),
        ):
            JsonPathTranslator.validate(jsonpath)

    def test_descendant_at_start_rejected(self):
        """Test that descendant operator at the start is rejected."""
        # Note: This syntax causes a parse error in jsonpath-ng, which is also acceptable
        jsonpath = "..name"
        with pytest.raises(
            (ValueError, JsonPathParserError)
        ):  # Can be either ValueError from our validator or parse error
            JsonPathTranslator.validate(jsonpath)

    def test_complex_valid_path(self):
        """Test a complex but valid path with fields and indexes."""
        jsonpath = "$.data.events[0].properties.user.profile[2].details.name"
        result = JsonPathTranslator.validate(jsonpath)
        assert result == jsonpath

    def test_field_with_special_characters_valid(self):
        """Test that fields with special characters work (if supported by jsonpath-ng)."""
        jsonpath = "$.events[0]['field-name']"
        result = JsonPathTranslator.validate(jsonpath)
        assert result == jsonpath

    def test_nested_negative_index_invalid(self):
        """Test that negative indices for nested properties throw."""
        jsonpath = "$.events[0].nested[-1].attr"
        with pytest.raises(
            ValueError,
            match=re.escape("Negative indices are not supported: -1"),
        ):
            JsonPathTranslator.validate(jsonpath)
