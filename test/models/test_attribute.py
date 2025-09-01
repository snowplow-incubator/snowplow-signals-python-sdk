import pytest

from snowplow_signals import (
    AtomicProperty,
    Attribute,
    CriteriaInput,
    Criterion,
    EntityProperty,
    Event,
    EventProperty,
    PagePing,
    PageView,
    StructuredEvent,
)


class TestValidAttributes:
    def test_all_attributes_validate(self):
        Attribute(
            name="add_to_cart_events_count",
            type="int32",
            events=[
                Event(
                    vendor="com.snowplowanalytics.snowplow.ecommerce",
                    name="snowplow_ecommerce_action",
                    version="1-0-2",
                )
            ],
            aggregation="counter",
            criteria=CriteriaInput(
                all=[
                    Criterion(
                        property="unstruct_event_com_snowplowanalytics_snowplow_ecommerce_snowplow_ecommerce_action_1:type",
                        operator="=",
                        value="add_to_cart",
                    )
                ],
            ),
        )

        Attribute(
            name="max_cart_value",
            type="float",
            events=[
                Event(
                    vendor="com.snowplowanalytics.snowplow.ecommerce",
                    name="snowplow_ecommerce_action",
                    version="1-0-2",
                )
            ],
            aggregation="max",
            property="contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1[0].total_value",
            criteria=CriteriaInput(
                all=[
                    Criterion(
                        property="unstruct_event_com_snowplowanalytics_snowplow_ecommerce_snowplow_ecommerce_action_1:type",
                        operator="=",
                        value="add_to_cart",
                    )
                ],
            ),
        )

        expensive_products_count = Attribute(
            name="expensive_products_count",
            type="int32",
            aggregation="counter",
            events=[
                Event(
                    vendor="com.snowplowanalytics.snowplow.ecommerce",
                    name="snowplow_ecommerce_action",
                    version="1-0-2",
                )
            ],
            criteria=CriteriaInput(
                all=[
                    Criterion(
                        property="unstruct_event_com_snowplowanalytics_snowplow_ecommerce_snowplow_ecommerce_action_1:type",
                        operator="=",
                        value="add_to_cart",
                    ),
                    Criterion(
                        property="contexts_com_snowplowanalytics_snowplow_ecommerce_product_1[0].price",
                        operator=">",
                        value=100,
                    ),
                ],
            ),
        )
        assert expensive_products_count.criteria is not None
        assert expensive_products_count.criteria.all is not None
        assert len(expensive_products_count.criteria.all) == 2


class TestInvalidAttributes:
    def test_invalid_name(self):
        with pytest.raises(ValueError):
            Attribute(
                name="add_to_cart_events_count!",
                type="int32",
                events=[
                    Event(
                        vendor="com.snowplowanalytics.snowplow.ecommerce",
                        name="snowplow_ecommerce_action",
                        version="1-0-2",
                    )
                ],
                aggregation="counter",
                criteria=CriteriaInput(
                    all=[
                        Criterion(
                            property="unstruct_event_com_snowplowanalytics_snowplow_ecommerce_snowplow_ecommerce_action_1:type",
                            operator="=",
                            value="add_to_cart",
                        )
                    ],
                ),
            )

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            Attribute(
                name="max_cart_value",
                type="float39",  # type: ignore
                events=[
                    Event(
                        vendor="com.snowplowanalytics.snowplow.ecommerce",
                        name="snowplow_ecommerce_action",
                        version="1-0-2",
                    )
                ],
                aggregation="max",
                property="contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1[0].total_value",
            )

    def test_invalid_aggregation(self):
        with pytest.raises(ValueError):
            Attribute(
                name="products_count",
                type="int32",
                aggregation="count",  # type: ignore
                events=[
                    Event(
                        vendor="com.snowplowanalytics.snowplow.ecommerce",
                        name="snowplow_ecommerce_action",
                        version="1-0-2",
                    )
                ],
            )

    def test_invalid_criterion_operator(self):
        with pytest.raises(ValueError):
            Attribute(
                name="products_count",
                type="int32",
                aggregation="count",  # type: ignore
                events=[
                    Event(
                        vendor="com.snowplowanalytics.snowplow.ecommerce",
                        name="snowplow_ecommerce_action",
                        version="1-0-2",
                    )
                ],
                criteria=CriteriaInput(
                    all=[
                        Criterion(
                            property="unstruct_event_com_snowplowanalytics_snowplow_ecommerce_snowplow_ecommerce_action_1:type",
                            operator="equals",  # type: ignore
                            value="add_to_cart",
                        )
                    ],
                ),
            )


class TestValidPropertyWrappers:
    def test_valid_entity_property(self):
        attribute = Attribute(
            name="max_cart_value",
            type="int32",
            events=[
                Event(
                    vendor="com.snowplowanalytics.snowplow.ecommerce",
                    name="snowplow_ecommerce_action",
                    version="1-0-2",
                )
            ],
            aggregation="max",
            property=EntityProperty(
                vendor="com.snowplowanalytics.snowplow.ecommerce",
                name="cart",
                major_version=1,
                path="total_value",
            ),
        )
        assert (
            attribute.property
            == "contexts_com_snowplowanalytics_snowplow_ecommerce_cart_1[0].total_value"
        )

    def test_valid_event_property(self):
        attribute = Attribute(
            name="first_button_click_label",
            type="string",
            events=[
                Event(
                    vendor="com.snowplowanalytics.snowplow",
                    name="button_click",
                    version="1-0-0",
                )
            ],
            aggregation="first",
            property=EventProperty(
                vendor="com.snowplowanalytics.snowplow",
                name="button_click",
                major_version=1,
                path="label",
            ),
        )
        assert (
            attribute.property
            == "unstruct_event_com_snowplowanalytics_snowplow_button_click_1:label"
        )

    def test_valid_atomic_property(self):
        attribute = Attribute(
            name="last_mkt_source",
            type="string",
            events=[
                Event(
                    vendor="com.snowplowanalytics.snowplow",
                    name="link_click",
                    version="1-0-1",
                )
            ],
            aggregation="last",
            property=AtomicProperty(name="mkt_source"),
        )
        assert attribute.property == "mkt_source"


class TestValidEventWrappers:
    def test_valid_page_view_event(self):
        last_mkt_source_page_view = Attribute(
            name="last_mkt_source",
            type="string",
            events=[PageView()],
            aggregation="last",
            property=AtomicProperty(name="mkt_source"),
        )
        assert last_mkt_source_page_view.events[0].name == "page_view"
        assert (
            last_mkt_source_page_view.events[0].vendor
            == "com.snowplowanalytics.snowplow"
        )
        assert last_mkt_source_page_view.events[0].version == "1-0-0"

    def test_valid_page_ping_event(self):
        last_mkt_source_page_ping = Attribute(
            name="last_mkt_source",
            type="string",
            events=[PagePing()],
            aggregation="last",
            property=AtomicProperty(name="mkt_source"),
        )
        assert last_mkt_source_page_ping.events[0].name == "page_ping"
        assert (
            last_mkt_source_page_ping.events[0].vendor
            == "com.snowplowanalytics.snowplow"
        )
        assert last_mkt_source_page_ping.events[0].version == "1-0-0"

    def test_valid_structured_event(self):
        last_mkt_source_structured_event = Attribute(
            name="last_mkt_source",
            type="string",
            events=[StructuredEvent()],
            aggregation="last",
            property=AtomicProperty(name="mkt_source"),
            criteria=CriteriaInput(
                all=[Criterion.eq(AtomicProperty(name="se_category"), "marketing")]
            ),
        )
        assert last_mkt_source_structured_event.events[0].name == "event"
        assert (
            last_mkt_source_structured_event.events[0].vendor == "com.google.analytics"
        )
        assert last_mkt_source_structured_event.events[0].version == "1-0-0"
