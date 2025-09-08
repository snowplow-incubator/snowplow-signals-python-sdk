from datetime import timedelta
from typing import Any

import pandas as pd

from .api_client import ApiClient
from .attributes_client import AttributesClient
from .interventions_client import InterventionsClient
from .models import (
    AttributeGroup,
    AttributeGroupResponse,
    AttributeKey,
    AttributeKeyId,
    AttributeKeyIdentifiers,
    InterventionInstance,
    RuleIntervention,
    Service,
    TestAttributeGroupRequest,
)
from .registry_client import RegistryClient
from .testing_client import TestingClient


class Signals:
    """Interface to interact with Snowplow Signals AI"""

    def __init__(self, *, api_url: str, api_key: str, api_key_id: str, org_id: str):
        # TODO, if not enough args raise and send to documentation ?
        self.api_client = ApiClient(
            api_url=api_url, api_key=api_key, api_key_id=api_key_id, org_id=org_id
        )

        self.interventions = InterventionsClient(api_client=self.api_client)
        self.registry = RegistryClient(api_client=self.api_client)
        self.attributes = AttributesClient(api_client=self.api_client)
        self.testing = TestingClient(api_client=self.api_client)

    def publish(
        self, objects: list[AttributeGroup | Service | AttributeKey | RuleIntervention]
    ) -> list[AttributeGroup | Service | AttributeKey | RuleIntervention]:
        """
        Creates or updates the provided objects in the Signals registry and publishes them to the compute engines.

        Args:
            objects: The list of objects to publish.
        Returns:
            The list of updated objects
        """
        to_update = [
            object.model_copy(update={"is_published": True}) for object in objects
        ]

        updated_objects = self.registry.create_or_update(objects=to_update)
        return updated_objects

    def unpublish(
        self, objects: list[AttributeGroup | Service | AttributeKey | RuleIntervention]
    ) -> list[AttributeGroup | Service | AttributeKey | RuleIntervention]:
        """
        Creates or updates the provided objects in the Signals registry and unpublishes them from the compute engines.

        Args:
            objects: The list of objects to unpublish.
        Returns:
            The list of unpublished objects
        """
        to_update = [
            object.model_copy(update={"is_published": False}) for object in objects
        ]

        updated_objects = self.registry.create_or_update(objects=to_update)
        return updated_objects

    def delete(
        self, objects: list[AttributeGroup | Service | AttributeKey | RuleIntervention]
    ) -> None:
        """
        Deletes the provided objects from the Signals registry.
        Make sure to unpublish the objects first.

        Args:
            objects: The list of objects to delete.
        Returns:
            The list of deleted objects
        """
        self.registry.delete(objects=objects)

    def get_attribute_group(
        self, name: str, version: int | None = None
    ) -> AttributeGroupResponse:
        """
        Returns an Attribute Group from the Signals registry by name.
        If no version is provided, returns the latest one.

        Args:
            name: The name of the Attribute Group.
            version: The version of the Attribute Group.
        Returns:
            The Attribute Group
        """
        attribute_group = self.registry.get_attribute_group(name, version)
        return attribute_group

    def get_group_attributes(
        self,
        name: str,
        version: int,
        attributes: list[str] | str,
        attribute_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        """
        Retrieves the attributes for a given attribute group by name and version.

        Args:
            name: The name of the attribute group.
            version: The version of the attribute group.
            attribute_key: The attribute_key name to retrieve attributes for.
            identifier: The attribute key identifier to retrieve attributes for.
            attributes: The list of attributes to retrieve.
        """
        return self.attributes.get_group_attributes(
            name=name,
            version=version,
            attributes=attributes,
            attribute_key=attribute_key,
            identifier=identifier,
        )

    def get_service_attributes(
        self,
        name: str,
        attribute_key: str,
        identifier: str,
    ) -> dict[str, Any]:
        """
        Retrieves the attributes for a given service by name.

        Args:
            name: The name of the Service.
            attribute_key: The attribute_key to retrieve attributes for.
            identifier: The attribute key identifier to retrieve attributes for.
        """
        return self.attributes.get_service_attributes(
            name=name,
            attribute_key=attribute_key,
            identifier=identifier,
        )

    def test(
        self,
        attribute_group: AttributeGroup,
        attribute_key_ids: list[AttributeKeyId] = [],
        app_ids: list[str] = [],
        window: timedelta = timedelta(hours=1),
    ) -> pd.DataFrame:
        """
        Tests the attribute group by extracting the features from the latest window of events in the atomic events table in warehouse.

        Args:
            attribute_group: The attribute group to test.
            attribute_key_ids: The list of attribute key ids (e.g., domain_userid values) to extract features for. If empty, random 10 IDs will be used.
            app_ids: The list of app ids to extract features for.
            window: The time window to extract features from.
        """
        request = TestAttributeGroupRequest(
            attribute_group=attribute_group,
            attribute_key_ids=attribute_key_ids,
            window=window,
            app_ids=app_ids,  # pyright: ignore[reportArgumentType] AppID is already a string, validation happens at runtime
        )
        return self.testing.test_attribute_group(request=request)

    def push_intervention(
        self, targets: AttributeKeyIdentifiers, intervention: InterventionInstance
    ):
        """
        Publish the given intervention to any active subscribers for the given lists of Attribute Keys.

        Args:
            targets: Mapping of Attribute Keys to identifiers to send the intervention to.
            intervention: The intervention payload to publish to the target subscribers.
        Returns:
            Status detailing if the intervention was received by any subscribers.
        """
        return self.interventions.publish(intervention, targets)

    def pull_interventions(self, targets: AttributeKeyIdentifiers):
        """
        Return a subscription for interventions targeting the given Attribute Key targets.

        Args:
            targets: Mapping of Attribute Keys to identifiers to receive interventions for.
        Returns:
            A subscription object that can be started or used as a context manager to receive interventions.
        """
        return self.interventions.subscribe(targets)
