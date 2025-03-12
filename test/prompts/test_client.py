import httpx
import pytest

from snowplow_signals import Signals

from .utils import get_create_prompt_response, get_prompt_response, get_prompts_response


def test_get_prompt(respx_mock):
    mock_prompt_response = get_prompt_response()
    respx_mock.get("http://localhost:8000/api/v1/prompts/my_prompt").mock(
        return_value=httpx.Response(200, json=mock_prompt_response)
    )
    signals = Signals(api_url="http://localhost:8000")
    prompt = signals.prompts.get("my_prompt")
    assert prompt.name == "foo_prompt"
    assert prompt.version == 5


def test_get_prompts(respx_mock):
    mock_prompts_response = get_prompts_response()
    respx_mock.get("http://localhost:8000/api/v1/prompts/").mock(
        return_value=httpx.Response(200, json=mock_prompts_response)
    )
    signals = Signals(api_url="http://localhost:8000")
    prompts = signals.prompts.list()
    assert len(prompts) == 2
    assert prompts[0].name == "foo_prompt"
    assert prompts[1].name == "bar_prompt"


def test_create_prompt(respx_mock):
    mock_prompt_create_response = get_create_prompt_response()
    respx_mock.post("http://localhost:8000/api/v1/prompts/").mock(
        return_value=httpx.Response(201, json=mock_prompt_create_response)
    )
    signals = Signals(api_url="http://localhost:8000")
    created_prompt = signals.prompts.create(
        prompt={
            "name": "foo_prompt",
            "prompt": "hello {{total_clicks}}",
            "features": [
                {"name": "total_clicks", "reference": "ecommerce_features:total_clicks"}
            ],
            "labels": ["production"],
            "tags": ["string"],
            "author": "string",
            "commit_msg": "",
            "version": 2,
        }
    )
    assert created_prompt.name == "foo_prompt"
    assert created_prompt.version == 2
    assert hasattr(created_prompt, "created_at")
    assert hasattr(created_prompt, "updated_at")
    assert hasattr(created_prompt, "id")


def test_delete_prompt(respx_mock):
    mock_delete_prompt_response = {"ok": True}
    respx_mock.delete("http://localhost:8000/api/v1/prompts/my_prompt/version/1").mock(
        return_value=httpx.Response(200, json=mock_delete_prompt_response)
    )
    signals = Signals(api_url="http://localhost:8000")
    prompt_deleted = signals.prompts.delete("my_prompt", 1)
    assert prompt_deleted.ok is True


def test_hydrate_prompt(respx_mock):
    mock_hydrate_prompt_response = {"prompt": "hello 5, the count is 10"}
    respx_mock.post("http://localhost:8000/api/v1/prompts/foo_prompt/hydrate").mock(
        return_value=httpx.Response(200, json=mock_hydrate_prompt_response)
    )
    signals = Signals(api_url="http://localhost:8000")
    prompt_hydrated = signals.prompts.hydrate(
        "foo_prompt", session="test_session", user="test_user"
    )
    assert prompt_hydrated.prompt == "hello 5, the count is 10"


def test_hydrate_prompt_input(respx_mock):
    respx_mock.post("http://localhost:8000/api/v1/prompts/foo_prompt/hydrate").mock()

    with pytest.raises(
        ValueError, match="At least one of `session` or `user` must be provided."
    ):
        signals = Signals(api_url="http://localhost:8000")
        signals.prompts.hydrate("foo_prompt", session=None, user=None)
