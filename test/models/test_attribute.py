from snowplow_signals import Attribute, Event, Criteria, Criterion
import pytest


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
            criteria=Criteria(
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
            criteria=Criteria(
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
            criteria=Criteria(
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
                criteria=Criteria(
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
                type="float39",
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
                aggregation="count",
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
                aggregation="count",
                events=[
                    Event(
                        vendor="com.snowplowanalytics.snowplow.ecommerce",
                        name="snowplow_ecommerce_action",
                        version="1-0-2",
                    )
                ],
                criteria=Criteria(
                    all=[
                        Criterion(
                            property="unstruct_event_com_snowplowanalytics_snowplow_ecommerce_snowplow_ecommerce_action_1:type",
                            operator="equals",
                            value="add_to_cart",
                        )
                    ],
                ),
            )
