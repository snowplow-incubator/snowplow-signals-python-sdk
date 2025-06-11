import operator

import pytest

from snowplow_signals import Column, Criteria


def test_atomic_field_references():
    duid = Column("domain_userid")
    duid2 = Column.atomic("domain_userid")
    criteria = duid == "abc123"

    assert duid.__dict__ == duid2.__dict__
    assert isinstance(criteria, Criteria)
    assert criteria.all is not None

    criterion = criteria.all[0]
    assert criterion.property == "domain_userid"
    assert criterion.operator == "="
    assert criterion.value == "abc123"


def test_event_references():
    sde = Column.event(vendor="com.example", name="event")
    criteria = sde["test"] == "abc123"

    assert isinstance(criteria, Criteria)
    assert criteria.all is not None

    criterion = criteria.all[0]
    assert criterion.property == "unstruct_event_com_example_event_1:test"
    assert criterion.operator == "="
    assert criterion.value == "abc123"


def test_entity_references():
    sde = Column.entity(vendor="com.example", name="entity")
    criteria = sde["test"] >= 0

    assert isinstance(criteria, Criteria)
    assert criteria.all is not None

    criterion = criteria.all[0]
    assert criterion.property == "contexts_com_example_entity_1[0].test"
    assert criterion.operator == ">="
    assert criterion.value == 0


def test_operations():
    duid = Column("domain_userid")

    operations = {
        "=": (operator.eq, "abc123"),
        "!=": (operator.ne, "abc123"),
        ">": (operator.gt, 0),
        "<": (operator.lt, 0),
        ">=": (operator.ge, 0),
        "<=": (operator.le, 0),
        "like": (operator.mod, "blah%123"),
        "in": (operator.lshift, [0, 1, 2]),
    }

    for op, (fn, val) in operations.items():
        criteria = fn(duid, val)

        assert isinstance(criteria, Criteria)
        assert criteria.all is not None

        criterion = criteria.all[0]
        assert criterion.property == "domain_userid"
        assert criterion.operator == op
        assert criterion.value == val

    custom_ops = (duid << [0, 1, 2]) & (duid % "abc")
    assert custom_ops.all is not None
    assert len(custom_ops.all) == 2
    assert custom_ops.all[0].operator == "in"
    assert custom_ops.all[1].operator == "like"


def test_criteria_type_checks():
    sde = Column.entity(vendor="com.example", name="entity")

    with pytest.raises(TypeError):
        _ = sde["test"] > "a"


def test_criteria_grouping():
    duid = Column("domain_userid")
    sid = Column("domain_sessionid")

    criteria = (duid == "abc123") & (sid == "ses1")
    assert isinstance(criteria, Criteria)
    assert criteria.all is not None
    assert criteria.any is None
    assert len(criteria.all) == 2

    criteria = (duid == "abc123") | (sid == "ses1")
    assert isinstance(criteria, Criteria)
    assert criteria.all is None
    assert criteria.any is not None
    assert len(criteria.any) == 2

    all_criteria = (duid == "abc123") & (sid == "ses1")
    any_criteria = (duid == "abc456") | (sid == "ses2")

    with pytest.raises(TypeError):
        _ = all_criteria | any_criteria  # we can't mix "all" and "any"
    with pytest.raises(TypeError):
        _ = any_criteria & all_criteria  # we can't mix "any" and "all"
    with pytest.raises(TypeError):
        _ = all_criteria | (sid == "")  # we can't demote a previous "all" to an "any"
    with pytest.raises(TypeError):
        _ = any_criteria & (sid == "")  # we can't promote a previous "any" to an "all"

    # combining same types is fine
    all_criteria &= all_criteria
    any_criteria |= any_criteria
