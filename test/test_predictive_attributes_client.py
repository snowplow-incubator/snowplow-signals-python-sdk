import json
from datetime import datetime, timedelta

import httpx
import pytest
from respx import MockRouter

from snowplow_signals import (
    AttributeGroup,
    Criteria,
    Criterion,
    PredictiveAttribute,
    PredictiveAttributeResponse,
    PredictiveAttributeTraining,
    PredictiveAttributeTrainingError,
    Signals,
    SignalsAPIError,
    SourceGroupReference,
    TrainingRunStatus,
    TrainingSpan,
    domain_sessionid,
)
from snowplow_signals.models import AtomicProperty

BASE = "http://localhost:8000/api/v1"
PA_URL = f"{BASE}/registry/predictive_attributes"


@pytest.fixture
def predictive_attribute() -> PredictiveAttribute:
    return PredictiveAttribute(
        name="purchase_propensity",
        version=2,
        owner="test@example.com",
        description="Likelihood to purchase",
        input_attributes=[
            SourceGroupReference(
                name="session_stats", version=1, attribute_name="page_views"
            )
        ],
        goal_criteria=Criteria(
            all=[
                Criterion(
                    property=AtomicProperty(name="event_name"),
                    operator="=",
                    value="transaction",
                )
            ]
        ),
    )


def pa_response(pa: PredictiveAttribute, **overrides) -> dict:
    return {
        **pa.model_dump(mode="json", exclude_none=True),
        "full_name": f"{pa.name}_v{pa.version}",
        "is_published": False,
        "trainings": [],
        **overrides,
    }


def training_response(**overrides) -> dict:
    return {
        "version": 0,
        "status": "pending",
        "preset": "fast",
        "training_data_start": "2026-09-01T00:00:00",
        "training_data_end": "2026-10-01T00:00:00",
        **overrides,
    }


class TestCreatePredictiveAttribute:
    def test_creates_new_predictive_attribute(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        create_mock = respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(200, json=pa_response(predictive_attribute))
        )

        response = signals_client.create_predictive_attribute(predictive_attribute)

        body = json.loads(create_mock.calls[0].request.content)
        assert body["input_attributes"] == [
            {"name": "session_stats", "version": 1, "attribute_name": "page_views"}
        ]
        assert "is_published" not in body
        assert response.full_name == "purchase_propensity_v2"

    def test_updates_description_and_owner_when_definition_unchanged(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(400, json={"detail": "already exists"})
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200,
                json=pa_response(predictive_attribute, description="Old description"),
            )
        )
        update_mock = respx_mock.put(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(200, json=pa_response(predictive_attribute))
        )

        response = signals_client.create_predictive_attribute(predictive_attribute)

        assert json.loads(update_mock.calls[0].request.content) == {
            "description": "Likelihood to purchase",
            "owner": "test@example.com",
        }
        assert response.description == "Likelihood to purchase"

    def test_raises_when_existing_version_has_different_inputs(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(400, json={"detail": "already exists"})
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200,
                json=pa_response(
                    predictive_attribute,
                    input_attributes=[
                        {
                            "name": "session_stats",
                            "version": 1,
                            "attribute_name": "other_attribute",
                        }
                    ],
                ),
            )
        )
        update_mock = respx_mock.put(f"{PA_URL}/purchase_propensity/versions/2")

        with pytest.raises(ValueError, match="bump the version"):
            signals_client.create_predictive_attribute(predictive_attribute)

        assert not update_mock.called

    def test_raises_when_existing_version_has_different_goal(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(400, json={"detail": "already exists"})
        )
        existing = pa_response(predictive_attribute)
        existing["goal_criteria"]["all"][0]["value"] = "add_to_cart"
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(200, json=existing)
        )

        with pytest.raises(ValueError, match="bump the version"):
            signals_client.create_predictive_attribute(predictive_attribute)

    def test_raises_original_error_when_400_is_not_an_existing_version(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(400, json={"detail": "Invalid goal criteria"})
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(404, json={"detail": "not found"})
        )

        with pytest.raises(SignalsAPIError, match="Invalid goal criteria"):
            signals_client.create_predictive_attribute(predictive_attribute)

    def test_propagates_validation_errors(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(
                422, json={"detail": "Attribute group not found"}
            )
        )

        with pytest.raises(SignalsAPIError):
            signals_client.create_predictive_attribute(predictive_attribute)


class TestTrainPredictiveAttribute:
    def test_triggers_training(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        train_mock = respx_mock.post(
            f"{PA_URL}/purchase_propensity/versions/2/trainings"
        ).mock(return_value=httpx.Response(200, json=training_response()))

        training = signals_client.train_predictive_attribute(
            predictive_attribute,
            training_span=TrainingSpan(
                start_time=datetime(2026, 9, 1), end_time=datetime(2026, 10, 1)
            ),
            preset="thorough",
            max_negative_ratio=3.0,
        )

        body = json.loads(train_mock.calls[0].request.content)
        assert body["training_data_start"] == "2026-09-01T00:00:00"
        assert body["training_data_end"] == "2026-10-01T00:00:00"
        assert body["preset"] == "thorough"
        assert body["max_negative_ratio"] == 3.0
        assert training.status == TrainingRunStatus.PENDING
        assert training.version == 0

    def test_gets_training(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2/trainings/3").mock(
            return_value=httpx.Response(
                200, json=training_response(version=3, status="success")
            )
        )

        training = signals_client.get_predictive_attribute_training(
            predictive_attribute,
            training=PredictiveAttributeTraining.model_validate(
                training_response(version=3)
            ),
        )

        assert training.version == 3
        assert training.status == "success"


class TestGetPredictiveAttribute:
    def test_gets_latest_version(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity").mock(
            return_value=httpx.Response(200, json=pa_response(predictive_attribute))
        )

        response = signals_client.get_predictive_attribute("purchase_propensity")

        assert response.version == 2

    def test_training_statuses_compare_to_strings(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity").mock(
            return_value=httpx.Response(
                200,
                json=pa_response(
                    predictive_attribute,
                    trainings=[training_response(status="success")],
                ),
            )
        )

        response = signals_client.get_predictive_attribute("purchase_propensity")

        assert response.trainings[0].status == "success"
        assert response.trainings[0].preset == "fast"

    def test_gets_specific_version(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        get_mock = respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(200, json=pa_response(predictive_attribute))
        )

        signals_client.get_predictive_attribute("purchase_propensity", version=2)

        assert get_mock.called


class TestPublishPredictiveAttribute:
    def test_publish_creates_then_publishes_latest_training(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        response = pa_response(
            predictive_attribute,
            trainings=[training_response(version=0, status="success")],
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(200, json=response)
        )
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(200, json=response)
        )
        publish_mock = respx_mock.post(f"{BASE}/engines/publish").mock(
            return_value=httpx.Response(200, json={"status": "published"})
        )

        [published] = signals_client.publish([predictive_attribute])

        assert json.loads(publish_mock.calls[0].request.content) == {
            "predictive_attributes": [
                {"name": "purchase_propensity", "version": 2, "training_version": 0}
            ]
        }
        assert isinstance(published, PredictiveAttribute)
        assert published.is_published is True

    def test_publish_skips_engines_when_latest_training_already_published(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        response = pa_response(
            predictive_attribute,
            is_published=True,
            published_training_version=1,
            trainings=[
                training_response(version=0, status="success"),
                training_response(version=1, status="success"),
                training_response(version=2, status="failed"),
            ],
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(200, json=response)
        )
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(200, json=response)
        )
        publish_mock = respx_mock.post(f"{BASE}/engines/publish")

        signals_client.publish([predictive_attribute])

        assert not publish_mock.called

    def test_publish_runs_after_attribute_groups(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        group = AttributeGroup(
            name="session_stats",
            attribute_key=domain_sessionid,
            owner="test@example.com",
        )
        calls: list[str] = []

        def record(name: str, response: httpx.Response):
            def side_effect(request):
                calls.append(name)
                return response

            return side_effect

        respx_mock.post(f"{BASE}/registry/attribute_groups/").mock(
            side_effect=record(
                "group",
                httpx.Response(
                    200,
                    json={
                        "name": "session_stats",
                        "attribute_key": {"name": "domain_sessionid"},
                        "owner": "test@example.com",
                    },
                ),
            )
        )
        response = pa_response(
            predictive_attribute,
            trainings=[training_response(version=0, status="success")],
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            side_effect=record("pa_get", httpx.Response(200, json=response))
        )
        respx_mock.post(f"{PA_URL}/").mock(
            side_effect=record("pa", httpx.Response(200, json=response))
        )
        respx_mock.post(f"{BASE}/engines/publish").mock(
            side_effect=record(
                "pa_publish", httpx.Response(200, json={"status": "published"})
            )
        )

        signals_client.publish([predictive_attribute, group])

        assert calls == ["pa_get", "group", "pa", "pa_publish"]

    def test_unpublish_unpublishes_when_published(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200, json=pa_response(predictive_attribute, is_published=True)
            )
        )
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(200, json=pa_response(predictive_attribute))
        )
        unpublish_mock = respx_mock.post(f"{BASE}/engines/unpublish").mock(
            return_value=httpx.Response(200, json={"status": "unpublished"})
        )

        [unpublished] = signals_client.unpublish([predictive_attribute])

        assert json.loads(unpublish_mock.calls[0].request.content) == {
            "predictive_attributes": [{"name": "purchase_propensity", "version": 2}]
        }
        assert unpublished.is_published is False

    def test_unpublish_skips_engines_when_not_published(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(200, json=pa_response(predictive_attribute))
        )
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(200, json=pa_response(predictive_attribute))
        )
        unpublish_mock = respx_mock.post(f"{BASE}/engines/unpublish")

        signals_client.unpublish([predictive_attribute])

        assert not unpublish_mock.called

    def test_delete_deletes_version(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        delete_mock = respx_mock.delete(
            f"{PA_URL}/purchase_propensity/versions/2"
        ).mock(return_value=httpx.Response(200, json={"ok": True}))

        signals_client.delete([predictive_attribute])

        assert delete_mock.called


class TestPublishKeepsLiveTraining:
    def test_publish_does_not_change_live_training_but_warns(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        response = pa_response(
            predictive_attribute,
            is_published=True,
            published_training_version=0,
            trainings=[
                training_response(version=0, status="success"),
                training_response(version=1, status="success"),
            ],
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(200, json=response)
        )
        respx_mock.post(f"{PA_URL}/").mock(
            return_value=httpx.Response(200, json=response)
        )
        publish_mock = respx_mock.post(f"{BASE}/engines/publish")

        with pytest.warns(UserWarning, match="training v1 is newer") as record:
            signals_client.publish([predictive_attribute])

        assert record[0].filename == __file__
        assert not publish_mock.called


class TestUnpublishPredictiveAttribute:
    def test_unpublishes_fetched_predictive_attribute(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        fetched = PredictiveAttributeResponse.model_validate(
            pa_response(predictive_attribute)
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200, json=pa_response(predictive_attribute, is_published=True)
            )
        )
        unpublish_mock = respx_mock.post(f"{BASE}/engines/unpublish").mock(
            return_value=httpx.Response(200, json={"status": "unpublished"})
        )

        signals_client.unpublish_predictive_attribute(fetched)

        assert unpublish_mock.called


class TestUnpublishOrdering:
    def test_unpublish_runs_before_attribute_groups(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        group = AttributeGroup(
            name="session_stats",
            attribute_key=domain_sessionid,
            owner="test@example.com",
        )
        calls: list[str] = []

        def record(name: str, response: httpx.Response):
            def side_effect(request):
                calls.append(name)
                return response

            return side_effect

        respx_mock.post(f"{BASE}/registry/attribute_groups/").mock(
            side_effect=record(
                "group",
                httpx.Response(
                    200,
                    json={
                        "name": "session_stats",
                        "attribute_key": {"name": "domain_sessionid"},
                        "owner": "test@example.com",
                    },
                ),
            )
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            side_effect=record(
                "pa_get",
                httpx.Response(
                    200, json=pa_response(predictive_attribute, is_published=True)
                ),
            )
        )
        respx_mock.post(f"{PA_URL}/").mock(
            side_effect=record(
                "pa", httpx.Response(200, json=pa_response(predictive_attribute))
            )
        )
        respx_mock.post(f"{BASE}/engines/unpublish").mock(
            side_effect=record(
                "pa_unpublish", httpx.Response(200, json={"status": "unpublished"})
            )
        )

        signals_client.unpublish([group, predictive_attribute])

        assert calls == ["pa_get", "pa_unpublish", "group", "pa"]

    def test_unpublish_registers_new_predictive_attribute_after_groups(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        group = AttributeGroup(
            name="session_stats",
            attribute_key=domain_sessionid,
            owner="test@example.com",
        )
        calls: list[str] = []

        def record(name: str, response: httpx.Response):
            def side_effect(request):
                calls.append(name)
                return response

            return side_effect

        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            side_effect=record(
                "pa_get", httpx.Response(404, json={"detail": "not found"})
            )
        )
        respx_mock.post(f"{BASE}/registry/attribute_groups/").mock(
            side_effect=record(
                "group",
                httpx.Response(
                    200,
                    json={
                        "name": "session_stats",
                        "attribute_key": {"name": "domain_sessionid"},
                        "owner": "test@example.com",
                    },
                ),
            )
        )
        respx_mock.post(f"{PA_URL}/").mock(
            side_effect=record(
                "pa", httpx.Response(200, json=pa_response(predictive_attribute))
            )
        )
        unpublish_mock = respx_mock.post(f"{BASE}/engines/unpublish")

        signals_client.unpublish([group, predictive_attribute])

        assert calls == ["pa_get", "group", "pa"]
        assert not unpublish_mock.called


class TestPublishPredictiveAttributeTraining:
    def test_publishes_pinned_training_version(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200,
                json=pa_response(
                    predictive_attribute,
                    is_published=True,
                    published_training_version=3,
                    trainings=[
                        training_response(version=1, status="success"),
                        training_response(version=3, status="success"),
                    ],
                ),
            )
        )
        publish_mock = respx_mock.post(f"{BASE}/engines/publish").mock(
            return_value=httpx.Response(200, json={"status": "published"})
        )

        signals_client.publish_predictive_attribute(predictive_attribute, training=1)

        assert json.loads(publish_mock.calls[0].request.content) == {
            "predictive_attributes": [
                {"name": "purchase_propensity", "version": 2, "training_version": 1}
            ]
        }

    def test_skips_when_pinned_training_already_published(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200,
                json=pa_response(
                    predictive_attribute,
                    is_published=True,
                    published_training_version=1,
                    trainings=[
                        training_response(version=1, status="success"),
                        training_response(version=3, status="success"),
                    ],
                ),
            )
        )
        publish_mock = respx_mock.post(f"{BASE}/engines/publish")

        signals_client.publish_predictive_attribute(predictive_attribute, training=1)

        assert not publish_mock.called

    def test_raises_before_changes_when_no_successful_training(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        group = AttributeGroup(
            name="session_stats",
            attribute_key=domain_sessionid,
            owner="test@example.com",
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200,
                json=pa_response(
                    predictive_attribute,
                    trainings=[training_response(version=0, status="running")],
                ),
            )
        )
        group_mock = respx_mock.post(f"{BASE}/registry/attribute_groups/")
        create_mock = respx_mock.post(f"{PA_URL}/")
        publish_mock = respx_mock.post(f"{BASE}/engines/publish")

        with pytest.raises(ValueError, match="no successful training"):
            signals_client.publish([group, predictive_attribute])

        assert not group_mock.called
        assert not create_mock.called
        assert not publish_mock.called

    def test_raises_before_changes_when_definition_changed(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        group = AttributeGroup(
            name="session_stats",
            version=2,
            attribute_key=domain_sessionid,
            owner="test@example.com",
        )
        changed = predictive_attribute.model_copy(
            update={
                "input_attributes": [
                    SourceGroupReference(
                        name="session_stats", version=2, attribute_name="page_views"
                    )
                ]
            }
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200,
                json=pa_response(
                    predictive_attribute,
                    trainings=[training_response(version=0, status="success")],
                ),
            )
        )
        group_mock = respx_mock.post(f"{BASE}/registry/attribute_groups/")
        create_mock = respx_mock.post(f"{PA_URL}/")

        with pytest.raises(ValueError, match="bump the version"):
            signals_client.publish([group, changed])

        assert not group_mock.called
        assert not create_mock.called

    def test_unpublish_raises_before_changes_when_definition_changed(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        changed = predictive_attribute.model_copy(
            update={
                "goal_criteria": Criteria(
                    all=[Criterion.eq(AtomicProperty(name="event_name"), "x")]
                )
            }
        )
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(
                200, json=pa_response(predictive_attribute, is_published=True)
            )
        )
        unpublish_mock = respx_mock.post(f"{BASE}/engines/unpublish")

        with pytest.raises(ValueError, match="bump the version"):
            signals_client.unpublish([changed])

        assert not unpublish_mock.called

    def test_raises_before_changes_when_not_registered(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2").mock(
            return_value=httpx.Response(404, json={"detail": "not found"})
        )
        create_mock = respx_mock.post(f"{PA_URL}/")

        with pytest.raises(ValueError, match="no successful training"):
            signals_client.publish([predictive_attribute])

        assert not create_mock.called


class TestWaitForPredictiveAttributeTraining:
    def test_returns_training_once_successful(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        get_mock = respx_mock.get(
            f"{PA_URL}/purchase_propensity/versions/2/trainings/0"
        ).mock(
            side_effect=[
                httpx.Response(200, json=training_response(status="pending")),
                httpx.Response(200, json=training_response(status="running")),
                httpx.Response(200, json=training_response(status="success")),
            ]
        )

        training = signals_client.wait_for_predictive_attribute_training(
            predictive_attribute, training=0, poll_interval=timedelta(0)
        )

        assert training.status == "success"
        assert get_mock.call_count == 3

    def test_raises_with_error_when_training_fails(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2/trainings/0").mock(
            return_value=httpx.Response(
                200,
                json=training_response(status="failed", error="Not enough data"),
            )
        )

        with pytest.raises(
            PredictiveAttributeTrainingError, match="Not enough data"
        ) as exc_info:
            signals_client.wait_for_predictive_attribute_training(
                predictive_attribute, training=0, poll_interval=timedelta(0)
            )

        assert exc_info.value.training.status == "failed"

    def test_raises_timeout_when_training_does_not_finish(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        respx_mock.get(f"{PA_URL}/purchase_propensity/versions/2/trainings/0").mock(
            return_value=httpx.Response(200, json=training_response(status="running"))
        )

        with pytest.raises(TimeoutError):
            signals_client.wait_for_predictive_attribute_training(
                predictive_attribute,
                training=0,
                timeout=timedelta(0),
                poll_interval=timedelta(0),
            )


def stats_response(**overrides) -> dict:
    return {
        "total_rows": 5000,
        "training_rows": 5000,
        "positive_rows": 800,
        "negative_rows": 4200,
        "positive_sessions": 200,
        "negative_sessions": 1500,
        "train": {"positive_sessions": 150, "negative_sessions": 1200},
        "eval": {"positive_sessions": 50, "negative_sessions": 300},
        "has_enough_data": True,
        "shortfalls": [],
        **overrides,
    }


class TestTestPredictiveAttribute:
    def test_previews_dataset_without_creating(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        test_mock = respx_mock.post(f"{BASE}/testing/predictive_attributes/").mock(
            return_value=httpx.Response(200, json=stats_response())
        )

        stats = signals_client.test_predictive_attribute(
            predictive_attribute,
            training_span=TrainingSpan(
                start_time=datetime(2026, 9, 1), end_time=datetime(2026, 10, 1)
            ),
            min_events=2,
        )

        body = json.loads(test_mock.calls[0].request.content)
        assert body["predictive_attribute"]["name"] == "purchase_propensity"
        assert body["predictive_attribute"]["input_attributes"] == [
            {"name": "session_stats", "version": 1, "attribute_name": "page_views"}
        ]
        assert "is_published" not in body["predictive_attribute"]
        assert body["training"]["training_data_start"] == "2026-09-01T00:00:00"
        assert body["training"]["training_data_end"] == "2026-10-01T00:00:00"
        assert body["training"]["min_events"] == 2
        assert stats.has_enough_data is True
        assert stats.train.positive_sessions == 150

    def test_returns_shortfalls(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        message = "Not enough data: 0 positive sessions in train split (minimum 50)"
        respx_mock.post(f"{BASE}/testing/predictive_attributes/").mock(
            return_value=httpx.Response(
                200,
                json=stats_response(
                    has_enough_data=False,
                    shortfalls=[
                        {
                            "measure": "positive_sessions",
                            "split": "train",
                            "actual": 0,
                            "minimum": 50,
                            "message": message,
                        }
                    ],
                ),
            )
        )

        stats = signals_client.test_predictive_attribute(
            predictive_attribute,
            training_span=TrainingSpan(
                start_time=datetime(2026, 9, 1), end_time=datetime(2026, 10, 1)
            ),
        )

        assert stats.has_enough_data is False
        assert stats.shortfalls[0].split == "train"
        assert stats.shortfalls[0].message == message

    def test_accepts_fetched_predictive_attribute(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        fetched = PredictiveAttributeResponse.model_validate(
            pa_response(
                predictive_attribute,
                trainings=[training_response(version=0, status="success")],
            )
        )
        test_mock = respx_mock.post(f"{BASE}/testing/predictive_attributes/").mock(
            return_value=httpx.Response(200, json=stats_response())
        )

        signals_client.test_predictive_attribute(
            fetched,
            training_span=TrainingSpan(
                start_time=datetime(2026, 9, 1), end_time=datetime(2026, 10, 1)
            ),
        )

        body = json.loads(test_mock.calls[0].request.content)
        assert "trainings" not in body["predictive_attribute"]
        assert "full_name" not in body["predictive_attribute"]


class TestGetPredictiveAttributeScore:
    def test_gets_score_for_predictive_attribute(
        self,
        respx_mock: MockRouter,
        signals_client: Signals,
        predictive_attribute: PredictiveAttribute,
    ):
        score_mock = respx_mock.get(f"{BASE}/predictive_attribute").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "purchase_propensity",
                    "version": 2,
                    "minor_version": 0,
                    "score": 0.42,
                },
            )
        )

        score = signals_client.get_predictive_attribute_score(
            predictive_attribute.name, identifiers={"domain_sessionid": "abc"}
        )

        params = score_mock.calls[0].request.url.params
        assert params["name"] == "purchase_propensity"
        assert params["domain_sessionid"] == "abc"
        assert score.score == pytest.approx(0.42)


def test_dataset_event_is_exported():
    from snowplow_signals import DatasetEvent

    assert DatasetEvent(name="page_ping").name == "page_ping"
