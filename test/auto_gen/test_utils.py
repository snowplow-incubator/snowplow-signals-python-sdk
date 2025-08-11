import pytest

from snowplow_signals.batch_autogen.models.modeling_step import (
    FilterCondition,
)
from snowplow_signals.batch_autogen.utils.utils import get_condition_sql


@pytest.mark.parametrize(
    "conditions, condition_type, expected_sql",
    [
        (
            [FilterCondition(operator="=", property="age", value=30)],
            "AND",
            " age = 30",
        ),
        (
            [FilterCondition(operator="!=", property="country", value="USA")],
            "AND",
            " (country != 'USA' or country is null)",
        ),
        (
            [FilterCondition(operator="like", property="name", value="John")],
            "AND",
            " name LIKE '%John%'",
        ),
        (
            [FilterCondition(operator="in", property="id", value="1,2,3")],
            "OR",
            " id IN(1,2,3)",
        ),
    ],
)
def test_get_condition_sql(conditions, condition_type, expected_sql):
    sql = get_condition_sql(conditions, condition_type)
    assert sql == expected_sql


def test_invalid_comparison_with_string():
    conditions = [FilterCondition(operator=">", property="name", value="banana")]

    with pytest.raises(
        ValueError,
        match="Cannot apply comparison operator '>' on a string value: 'banana'",
    ):
        get_condition_sql(conditions, "AND")
