import json
from datetime import datetime, timezone

import httpx
import pytest
from respx import MockRouter

from snowplow_signals import (
    AttributeGroup,
    Criteria,
    Criterion,
    Event,
    Signals,
    domain_userid,
)
from snowplow_signals.api_client import ApiClient
from snowplow_signals.models import AtomicProperty
from snowplow_signals.models.dataset import (
    DatasetBundle,
    Output,
    SessionAnchors,
    TrainingSpan,
    UserSuppliedAnchors,
)


class TestDatasetModels:
    def test_session_anchors_serialization(self):
        from snowplow_signals.models.dataset import SessionAnchors, TrainingSpan

        anchors = SessionAnchors(
            goal_criteria=Criteria(
                any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
            ),
            keys=["domain_userid", "domain_sessionid"],
            training_span=TrainingSpan(
                start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2025, 6, 1, tzinfo=timezone.utc),
            ),
        )

        dumped = anchors.model_dump(mode="json", exclude_none=True, by_alias=True)
        assert dumped["mode"] == "session"
        assert dumped["keys"] == ["domain_userid", "domain_sessionid"]
        assert dumped["max_negative_ratio"] == 5.0
        assert dumped["min_events"] == 1
        assert dumped["excluded_events"] == ["page_ping"]
        assert "goal_criteria" in dumped
        assert "training_span" in dumped

    def test_user_supplied_anchors_serialization(self):
        from snowplow_signals.models.dataset import UserSuppliedAnchors

        anchors = UserSuppliedAnchors(
            source_table="db.schema.my_anchors",
            key_columns=["domain_userid"],
        )

        dumped = anchors.model_dump(mode="json", exclude_none=True, by_alias=True)
        assert dumped["mode"] == "user_supplied"
        assert dumped["source_table"] == "db.schema.my_anchors"
        assert dumped["key_columns"] == ["domain_userid"]
        assert dumped["has_label"] is True

    def test_output_serialization_uses_schema_alias(self):
        from snowplow_signals.models.dataset import Output

        output = Output(database="my_db", schema="my_schema")

        dumped = output.model_dump(mode="json", exclude_none=True, by_alias=True)
        assert dumped["schema"] == "my_schema"
        assert "schema_" not in dumped
        assert dumped["database"] == "my_db"
        assert dumped["anchors_table"] == "signals_anchors"

    def test_output_optional_fields_excluded_when_none(self):
        from snowplow_signals.models.dataset import Output

        output = Output()

        dumped = output.model_dump(mode="json", exclude_none=True, by_alias=True)
        assert "database" not in dumped
        assert "schema" not in dumped
        assert dumped["anchors_table"] == "signals_anchors"

    def test_dataset_bundle_save_to(self, tmp_path):
        from snowplow_signals.models.dataset import DatasetBundle

        bundle = DatasetBundle(
            files={
                "README.md": "# My Dataset",
                "anchors.sql": "SELECT 1;",
                "attributes.sql": "SELECT 2;",
            }
        )

        bundle.save_to(tmp_path / "output")

        assert (tmp_path / "output" / "README.md").read_text() == "# My Dataset"
        assert (tmp_path / "output" / "anchors.sql").read_text() == "SELECT 1;"
        assert (tmp_path / "output" / "attributes.sql").read_text() == "SELECT 2;"

    def test_dataset_bundle_save_to_creates_nested_dirs(self, tmp_path):
        from snowplow_signals.models.dataset import DatasetBundle

        bundle = DatasetBundle(files={"test.sql": "SELECT 1;"})
        nested = tmp_path / "a" / "b" / "c"

        bundle.save_to(nested)

        assert (nested / "test.sql").read_text() == "SELECT 1;"


class TestDatasetClient:
    def _make_session_anchors(self) -> SessionAnchors:
        return SessionAnchors(
            goal_criteria=Criteria(
                any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
            ),
            keys=["domain_userid", "domain_sessionid"],
            training_span=TrainingSpan(
                start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2025, 6, 1, tzinfo=timezone.utc),
            ),
        )

    def _make_attribute_group(self) -> AttributeGroup:
        return AttributeGroup(
            name="my_group",
            attribute_key=domain_userid,
            owner="test@example.com",
        )

    def _mock_bundle_response(self) -> dict:
        return {
            "files": [
                {"filename": "README.md", "content": "# Dataset"},
                {"filename": "anchors.sql", "content": "SELECT 1;"},
                {"filename": "attributes.sql", "content": "SELECT 2;"},
            ]
        }

    def test_build_sql_session_anchors_request(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        result = signals_client.build_dataset_sql(
            attribute_groups=[self._make_attribute_group()],
            anchors=self._make_session_anchors(),
            source_table="db.schema.events",
        )

        assert mock.called
        request_body = json.loads(mock.calls[0].request.content)
        assert request_body["source_table"] == "db.schema.events"
        assert request_body["anchors"]["mode"] == "session"
        assert request_body["anchors"]["keys"] == ["domain_userid", "domain_sessionid"]
        assert "training_span" in request_body["anchors"]
        assert len(request_body["attribute_groups"]) == 1
        assert request_body["attribute_groups"][0]["name"] == "my_group"

    def test_build_sql_user_supplied_anchors_request(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        anchors = UserSuppliedAnchors(
            source_table="db.schema.my_anchors",
            key_columns=["domain_userid"],
        )

        signals_client.build_dataset_sql(
            attribute_groups=[self._make_attribute_group()],
            anchors=anchors,
            source_table="db.schema.events",
        )

        request_body = json.loads(mock.calls[0].request.content)
        assert request_body["anchors"]["mode"] == "user_supplied"
        assert request_body["anchors"]["source_table"] == "db.schema.my_anchors"
        assert request_body["anchors"]["key_columns"] == ["domain_userid"]

    def test_build_sql_parses_bundle_response(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        result = signals_client.build_dataset_sql(
            attribute_groups=[self._make_attribute_group()],
            anchors=self._make_session_anchors(),
            source_table="db.schema.events",
        )

        assert isinstance(result, DatasetBundle)
        assert result.files == {
            "README.md": "# Dataset",
            "anchors.sql": "SELECT 1;",
            "attributes.sql": "SELECT 2;",
        }

    def test_build_sql_output_included_when_provided(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        signals_client.build_dataset_sql(
            attribute_groups=[self._make_attribute_group()],
            anchors=self._make_session_anchors(),
            source_table="db.schema.events",
            output=Output(database="my_db", schema="my_schema"),
        )

        request_body = json.loads(mock.calls[0].request.content)
        assert request_body["output"]["database"] == "my_db"
        assert request_body["output"]["schema"] == "my_schema"

    def test_build_sql_output_omitted_when_none(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        signals_client.build_dataset_sql(
            attribute_groups=[self._make_attribute_group()],
            anchors=self._make_session_anchors(),
            source_table="db.schema.events",
        )

        request_body = json.loads(mock.calls[0].request.content)
        assert "output" not in request_body


class TestDatasetExports:
    def test_models_importable_from_snowplow_signals(self):
        from snowplow_signals import (
            DatasetBundle,
            Output,
            SessionAnchors,
            TrainingSpan,
            UserSuppliedAnchors,
        )

        assert SessionAnchors is not None
        assert UserSuppliedAnchors is not None
        assert TrainingSpan is not None
        assert Output is not None
        assert DatasetBundle is not None
