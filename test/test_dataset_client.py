import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import httpx
from respx import MockRouter

from snowplow_signals import (
    AttributeGroup,
    Criteria,
    Criterion,
    Signals,
    domain_userid,
)
from snowplow_signals.dataset_client import DatasetClient
from snowplow_signals.models import (
    AtomicProperty,
    DatasetBundle,
    DatasetBundleRequest,
    DatasetBundleResponse,
    DatasetSqlFile,
    SessionAnchors,
    TrainingSpan,
    UserSuppliedAnchors,
    WarehouseTable,
)
from snowplow_signals.models.model import (
    AttributeKeyOutput,
    AttributeSqlFile,
    DatasetAttributeGroups,
)


class TestDatasetModels:
    def test_session_anchors_serialization(self):
        anchors = SessionAnchors(
            goal_criteria=Criteria(
                any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
            ),
            training_span=TrainingSpan(
                start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2025, 6, 1, tzinfo=timezone.utc),
            ),
        )

        dumped = anchors.model_dump(mode="json", exclude_none=True, by_alias=True)
        assert dumped["mode"] == "session"
        assert dumped["max_negative_ratio"] == 5.0
        assert dumped["min_events"] == 1
        assert dumped["excluded_events"] == [{"name": "page_ping"}]
        assert "goal_criteria" in dumped
        assert "training_span" in dumped

    def test_user_supplied_anchors_serialization(self):
        anchors = UserSuppliedAnchors(
            source=WarehouseTable(
                database="my_db", schema="my_schema", table="my_anchors"
            ),
            has_label=True,
        )

        dumped = anchors.model_dump(mode="json", exclude_none=True, by_alias=True)
        assert dumped["mode"] == "user_supplied"
        assert dumped["source"]["database"] == "my_db"
        assert dumped["source"]["schema"] == "my_schema"
        assert dumped["source"]["table"] == "my_anchors"
        assert dumped["has_label"] is True

    def test_warehouse_table_serialization_uses_schema_alias(self):
        table = WarehouseTable(database="my_db", schema="my_schema", table="my_table")

        dumped = table.model_dump(mode="json", exclude_none=True, by_alias=True)
        assert dumped["schema"] == "my_schema"
        assert "schema_" not in dumped
        assert dumped["database"] == "my_db"
        assert dumped["table"] == "my_table"

    def _make_session_anchors(self) -> SessionAnchors:
        return SessionAnchors(
            goal_criteria=Criteria(
                any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
            ),
            training_span=TrainingSpan(
                start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2025, 6, 1, tzinfo=timezone.utc),
            ),
        )

    def test_dataset_bundle_save_to(self, tmp_path):
        client = DatasetClient(api_client=MagicMock())
        bundle = DatasetBundle(
            request=DatasetBundleRequest(
                anchors=self._make_session_anchors(),
                attributes=DatasetAttributeGroups(
                    attribute_groups=[
                        AttributeGroup(
                            name="my_group",
                            attribute_key=domain_userid,
                            owner="test@example.com",
                        )
                    ],
                ),
            ),
            response=DatasetBundleResponse(
                anchors=DatasetSqlFile(
                    database="db",
                    schema="sch",
                    table="signals_anchors",
                    sql="SELECT 1;",
                ),
                attributes=[
                    AttributeSqlFile(
                        database="db",
                        schema="sch",
                        table="signals_attributes_domain_sessionid",
                        sql="SELECT 2;",
                        attribute_key=AttributeKeyOutput(
                            name="domain_sessionid", blobl_path=None
                        ),
                    )
                ],
                dataset=DatasetSqlFile(
                    database="db",
                    schema="sch",
                    table="signals_training_dataset",
                    sql="SELECT 3;",
                ),
            ),
            dataset_client=client,
        )

        bundle.save_to(tmp_path / "output")

        out = tmp_path / "output"
        assert (out / "signals_anchors.sql").read_text() == "SELECT 1;"
        assert (
            out / "signals_attributes_domain_sessionid.sql"
        ).read_text() == "SELECT 2;"
        assert (out / "signals_training_dataset.sql").read_text() == "SELECT 3;"

        # manifest.json is generated
        import json

        manifest = json.loads((out / "manifest.json").read_text())
        assert "generated_at" in manifest
        assert manifest["input"]["anchors"]["mode"] == "session"
        assert manifest["input"]["attribute_groups"] == [
            {"name": "my_group", "version": 1}
        ]
        # Output mirrors the API response structure (without sql)
        assert manifest["output"]["anchors"]["database"] == "db"
        assert manifest["output"]["anchors"]["schema"] == "sch"
        assert manifest["output"]["anchors"]["table"] == "signals_anchors"
        assert "sql" not in manifest["output"]["anchors"]
        assert len(manifest["output"]["attributes"]) == 1
        assert (
            manifest["output"]["attributes"][0]["table"]
            == "signals_attributes_domain_sessionid"
        )
        assert "sql" not in manifest["output"]["attributes"][0]
        assert manifest["output"]["dataset"]["table"] == "signals_training_dataset"
        assert "sql" not in manifest["output"]["dataset"]
        assert len(manifest["files"]) == 3

        # README.md is generated
        readme = (out / "README.md").read_text()
        assert "signals_anchors.sql" in readme
        assert "manifest.json" in readme

    def test_dataset_bundle_save_to_creates_nested_dirs(self, tmp_path):
        client = DatasetClient(api_client=MagicMock())
        bundle = DatasetBundle(
            request=DatasetBundleRequest(
                anchors=self._make_session_anchors(),
                attributes=DatasetAttributeGroups(
                    attribute_groups=[
                        AttributeGroup(
                            name="t",
                            attribute_key=domain_userid,
                            owner="test@example.com",
                        )
                    ],
                ),
            ),
            response=DatasetBundleResponse(
                anchors=DatasetSqlFile(
                    database=None, schema=None, table="anchors", sql="SELECT 1;"
                ),
                attributes=[],
                dataset=DatasetSqlFile(
                    database=None, schema=None, table="dataset", sql="SELECT 2;"
                ),
            ),
            dataset_client=client,
        )
        nested = tmp_path / "a" / "b" / "c"

        bundle.save_to(nested)

        assert (nested / "anchors.sql").read_text() == "SELECT 1;"


class TestDatasetClient:
    def _make_session_anchors(self) -> SessionAnchors:
        return SessionAnchors(
            goal_criteria=Criteria(
                any=[Criterion.eq(AtomicProperty(name="se_action"), "purchase")]
            ),
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
            "anchors": {
                "database": "db",
                "schema": "schema",
                "table": "signals_anchors",
                "sql": "SELECT 1;",
            },
            "attributes": [
                {
                    "database": "db",
                    "schema": "schema",
                    "table": "signals_attributes_domain_userid",
                    "sql": "SELECT 2;",
                    "attribute_key": {
                        "name": "domain_userid",
                        "blobl_path": None,
                    },
                }
            ],
            "dataset": {
                "database": "db",
                "schema": "schema",
                "table": "signals_training_dataset",
                "sql": "SELECT 3;",
            },
        }

    def test_build_sql_session_anchors_request(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        result = signals_client.build_dataset_with_session_anchors(
            attribute_groups=[self._make_attribute_group()],
            goal_criteria=self._make_session_anchors().goal_criteria,
            training_span=self._make_session_anchors().training_span,
        )

        assert mock.called
        request_body = json.loads(mock.calls[0].request.content)
        assert request_body["anchors"]["mode"] == "session"
        assert "training_span" in request_body["anchors"]
        assert len(request_body["attributes"]["attribute_groups"]) == 1
        assert request_body["attributes"]["attribute_groups"][0]["name"] == "my_group"

    def test_build_sql_parses_bundle_response(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        result = signals_client.build_dataset_with_session_anchors(
            attribute_groups=[self._make_attribute_group()],
            goal_criteria=self._make_session_anchors().goal_criteria,
            training_span=self._make_session_anchors().training_span,
        )

        assert isinstance(result, DatasetBundle)
        assert "signals_anchors.sql" in result.files
        assert "signals_attributes_domain_userid.sql" in result.files
        assert "signals_training_dataset.sql" in result.files

    def test_build_sql_dataset_included_when_provided(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        signals_client.build_dataset_with_session_anchors(
            attribute_groups=[self._make_attribute_group()],
            goal_criteria=self._make_session_anchors().goal_criteria,
            training_span=self._make_session_anchors().training_span,
            dataset_table=WarehouseTable(
                database="my_db", schema="my_schema", table="my_dataset"
            ),
        )

        request_body = json.loads(mock.calls[0].request.content)
        assert request_body["dataset"]["database"] == "my_db"
        assert request_body["dataset"]["schema"] == "my_schema"
        assert request_body["dataset"]["table"] == "my_dataset"

    def test_build_sql_dataset_omitted_when_none(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        signals_client.build_dataset_with_session_anchors(
            attribute_groups=[self._make_attribute_group()],
            goal_criteria=self._make_session_anchors().goal_criteria,
            training_span=self._make_session_anchors().training_span,
        )

        request_body = json.loads(mock.calls[0].request.content)
        assert "dataset" not in request_body

    def test_build_sql_user_supplied_anchors(
        self, respx_mock: MockRouter, signals_client: Signals
    ):
        mock = respx_mock.post("http://localhost:8000/api/v1/datasets/sql").mock(
            return_value=httpx.Response(200, json=self._mock_bundle_response())
        )

        signals_client.build_dataset_with_custom_anchors(
            attribute_groups=[self._make_attribute_group()],
            anchors_table=WarehouseTable(
                database="my_db", schema="my_schema", table="my_anchors"
            ),
        )

        request_body = json.loads(mock.calls[0].request.content)
        assert request_body["anchors"]["mode"] == "user_supplied"
        assert request_body["anchors"]["source"]["table"] == "my_anchors"


class TestDatasetExports:
    def test_models_importable_from_snowplow_signals(self):
        from snowplow_signals import (
            DatasetBundle,
            SessionAnchors,
            TrainingSpan,
            UserSuppliedAnchors,
            WarehouseTable,
        )

        assert SessionAnchors is not None
        assert UserSuppliedAnchors is not None
        assert WarehouseTable is not None
        assert TrainingSpan is not None
        assert DatasetBundle is not None
