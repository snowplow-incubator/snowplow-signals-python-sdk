from jsonpath_ng.ext import parse
from jsonpath_ng.jsonpath import (
    Descendants,
    Fields,
    Index,
    Root,
)


class JsonPathTranslator:
    @staticmethod
    def validate(path: str) -> str:
        """
        Validate the JSON path and return it in a format suitable for the Snowplow Signals API.
        """
        jsonpath_expr = parse(path)

        def walk(node):
            if isinstance(node, (Root, Fields, Index)):
                if isinstance(node, Index) and node.index < 0:
                    raise ValueError(
                        f"Negative indices are not supported: {node.index}"
                    )
                return
            elif isinstance(node, Descendants):
                raise ValueError(
                    f"Descendant operators (..) are not supported. Please use explicit paths only."
                )
            elif hasattr(node, "left") and hasattr(node, "right"):
                walk(node.left)
                walk(node.right)
            else:
                raise ValueError(
                    f"Unsupported JSONPath, please only use paths and indexes."
                )

        walk(jsonpath_expr)
        return path


def path_to_snowflake_syntax(path: str) -> str:
    """
    Translate a validated JSONPath to Snowflake object property access syntax.

    Args:
        path: A valid JSONPath expression

    Returns:
        A Snowflake-compatible property access string

    Examples:
        $.name -> name
        $.user.profile -> user.profile
        $.events[0] -> events[0]
        $.data.items[1].value -> data.items[1].value
    """

    # Ensure path starts with $. for validation
    validation_path = path if path.startswith("$.") else f"$.{path}"
    JsonPathTranslator.validate(validation_path)

    clean_path = path.lstrip("$.")

    return clean_path
