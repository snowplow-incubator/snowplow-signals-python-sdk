import ast
import re
from pathlib import Path

import snowplow_signals

README = Path(__file__).resolve().parent.parent / "README.md"


def _names_imported_in_readme() -> set[str]:
    code_blocks = re.findall(r"```python\n(.*?)```", README.read_text(), re.DOTALL)
    names: set[str] = set()
    for block in code_blocks:
        for node in ast.walk(ast.parse(block)):
            if isinstance(node, ast.ImportFrom) and node.module == "snowplow_signals":
                names.update(alias.name for alias in node.names)
    return names


def test_every_all_entry_is_importable():
    # Arrange
    exported = snowplow_signals.__all__

    # Act
    missing = [name for name in exported if not hasattr(snowplow_signals, name)]

    # Assert
    assert missing == []
    assert len(exported) == len(set(exported))


def test_all_covers_names_imported_in_readme():
    # Arrange
    readme_names = _names_imported_in_readme()

    # Act
    not_exported = readme_names - set(snowplow_signals.__all__)

    # Assert
    assert readme_names, "expected README to import from snowplow_signals"
    assert not_exported == set()
