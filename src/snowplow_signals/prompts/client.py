from typing import overload

from ..api_client import ApiClient
from .models.api import (
    EntityIdentifiers,
    PromptBase,
    PromptDeletedResponse,
    PromptHydrateResponse,
    PromptResponse,
)


class PromptsClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get(self, name: str, *, version: int | None = None) -> PromptResponse:
        response = self.api_client.make_request(
            method="GET",
            endpoint=(
                f"prompts/{name}/version/{version}" if version else f"prompts/{name}"
            ),
        )
        return PromptResponse(**response)

    def create(self, prompt: PromptBase) -> PromptResponse:
        prompt_input = PromptBase.model_validate(prompt)
        response = self.api_client.make_request(
            method="POST",
            endpoint="prompts/",
            data=prompt_input.model_dump(),
        )
        return PromptResponse(**response)

    def list(self) -> list[PromptResponse]:
        response = self.api_client.make_request(
            method="GET",
            endpoint="prompts/",
        )
        return [PromptResponse(**prompt) for prompt in response]

    def delete(self, name: str, version: int) -> PromptDeletedResponse:
        response = self.api_client.make_request(
            method="DELETE",
            endpoint=f"prompts/{name}/version/{version}",
        )
        return PromptDeletedResponse(**response)

    @overload
    def hydrate(
        self,
        name: str,
        *,
        session: str,
        version: int | None = None,
    ) -> PromptHydrateResponse: ...

    @overload
    def hydrate(
        self,
        name: str,
        *,
        user: str,
        version: int | None = None,
    ) -> PromptHydrateResponse: ...

    @overload
    def hydrate(
        self,
        name: str,
        *,
        session: str,
        user: str,
        version: int | None = None,
    ) -> PromptHydrateResponse: ...

    def hydrate(
        self,
        name: str,
        *,
        session: str | None = None,
        user: str | None = None,
        version: int | None = None,
    ) -> PromptHydrateResponse:
        if not session and not user:
            raise ValueError("At least one of `session` or `user` must be provided.")

        entity_identifiers = EntityIdentifiers(
            session=[session] if session else None, user=[user] if user else None
        )
        response = self.api_client.make_request(
            method="POST",
            endpoint=(
                f"prompts/{name}/version/{version}/hydrate"
                if version
                else f"prompts/{name}/hydrate"
            ),
            data=entity_identifiers.model_dump(exclude_none=True),
        )
        return PromptHydrateResponse(**response)
