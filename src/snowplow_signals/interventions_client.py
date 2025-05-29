from .api_client import ApiClient
from .models import RuleInterventionInput, RuleInterventionOutput


class InterventionsClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get(self, name: str, *, version: int | None = None) -> RuleInterventionOutput:
        response = self.api_client.make_request(
            method="GET",
            endpoint=(
                f"registry/interventions/{name}/versions/{version}"
                if version
                else f"registry/interventions/{name}"
            ),
        )
        return RuleInterventionOutput(**response)

    def list(self) -> list[RuleInterventionOutput]:
        response = self.api_client.make_request(
            method="GET",
            endpoint="registry/interventions/",
        )
        return [RuleInterventionOutput(**intervention) for intervention in response]

    def delete(self, name: str, version: int) -> dict[str, bool]:
        response = self.api_client.make_request(
            method="DELETE",
            endpoint=f"registry/interventions/{name}/versions/{version}",
        )
        return response

    def update(self, intervention: RuleInterventionInput) -> RuleInterventionOutput:
        response = self.api_client.make_request(
            method="PUT",
            endpoint=f"registry/interventions/{intervention.name}/versions/{intervention.version}",
            data=intervention.model_dump(
                mode="json",
                exclude_none=True,
                by_alias=True,
            ),
        )
        return RuleInterventionOutput(**response)

    def create(self, intervention: RuleInterventionInput) -> RuleInterventionOutput:
        response = self.api_client.make_request(
            method="POST",
            endpoint="registry/interventions/",
            data=intervention.model_dump(
                mode="json",
                exclude_none=True,
                by_alias=True,
            ),
        )
        return RuleInterventionOutput(**response)
