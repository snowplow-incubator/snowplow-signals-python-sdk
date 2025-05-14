from datetime import timedelta

import pandas as pd

from .api_client import ApiClient
from .attributes_client import AttributesClient
from .feature_store_client import FeatureStoreClient
from .models import (
    OnlineAttributesResponse,
    Service,
    TestViewRequest,
    View,
    ViewResponse,
)
from .prompts.client import PromptsClient
from .registry_client import RegistryClient
from .testing_client import TestingClient


class Signals:
    """Interface to interact with Snowplow Signals AI"""

    def __init__(self, *, api_url: str, api_key: str, api_key_id: str, org_id: str):
        # TODO, if not enough args raise and send to documentation ?
        self.api_client = ApiClient(
            api_url=api_url, api_key=api_key, api_key_id=api_key_id, org_id=org_id
        )

        self.prompts = PromptsClient(api_client=self.api_client)
        self.registry = RegistryClient(api_client=self.api_client)
        self.feature_store = FeatureStoreClient(api_client=self.api_client)
        self.attributes = AttributesClient(api_client=self.api_client)
        self.testing = TestingClient(api_client=self.api_client)

    def apply(self, objects: list[View | Service]) -> list[View | Service]:
        """
        Registers the provided objects to the Signals registry.

        Args:
            objects: The list of objects to register.
        Returns:
            The list of updated objects
        """
        updated_objets = self.registry.apply(objects=objects)
        self.feature_store.apply()
        return updated_objets

    def get_view(self, name: str, version: int | None = None) -> ViewResponse:
        """
        Returns a View from the Signals registry by name.
        If no version is provided, returns the latest one.

        Args:
            name: The name of the View.
            version: The version of the View.
        Returns:
            The View
        """
        view = self.registry.get_view(name, version)
        return view

    def get_online_attributes(
        self,
        source: Service | View | ViewResponse,
        identifiers: list[str] | str,
    ) -> OnlineAttributesResponse | None:
        """
        Retrieves the online attributes for a given source and identifiers.

        Args:
            source: Either a View or Service to retrieve attributes for.
            identifiers: The list of entity (user or session) identifiers to retrieve attributes for.
        """
        if isinstance(source, Service):
            return self.attributes.get_service_attributes(
                service=source,
                identifiers=identifiers,
            )
        elif isinstance(source, View) or isinstance(source, ViewResponse):
            return self.attributes.get_view_attributes(
                view=source,
                identifiers=identifiers,
            )
        else:
            raise TypeError("Source must be a FeatureService or a FeatureView.")

    def test(
        self,
        view: View,
        entity_ids: list[str] = [],
        app_ids: list[str] = [],
        window: timedelta = timedelta(hours=1),
    ) -> pd.DataFrame:
        """
        Tests the view by extracting the features from the latest window of events in the atomic events table in warehouse.

        Args:
            view: The feature view to test.
            entity_ids: The list of entity ids (e.g., domain_userid values) to extract features for. If empty, random 10 IDs will be used.
            app_ids: The list of app ids to extract features for.
            window: The time window to extract features from.
        """
        request = TestViewRequest(
            view=view,
            entity_ids=entity_ids,
            window=window,
            app_ids=app_ids,
        )
        return self.testing.test_view(request=request)
