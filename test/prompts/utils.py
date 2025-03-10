from typing import Any

mock_foo_prompt = {
    "name": "foo_prompt",
    "version": 5,
    "prompt": "hello {{products_added_to_cart}}, the count is {{total_clicks}}",
    "features": [
        {
            "name": "products_added_to_cart",
            "reference": "ecommerce_features:products_added_to_cart",
        },
        {"name": "total_clicks", "reference": "ecommerce_features:total_clicks"},
    ],
    "labels": ["production"],
    "tags": ["string"],
    "author": "string",
    "commit_msg": "",
    "id": "7e6e886e-4d4e-4267-9314-fc89c012fcf9",
    "created_at": "2025-03-01T12:54:01.366304Z",
    "updated_at": "2025-03-01T12:54:01.366304Z",
}

mock_foo_prompt_v2 = {
    "name": "foo_prompt",
    "version": 2,
    "prompt": "hello {{total_clicks}}",
    "features": [
        {"name": "total_clicks", "reference": "ecommerce_features:total_clicks"},
    ],
    "labels": ["production"],
    "tags": ["string"],
    "author": "string",
    "commit_msg": "",
    "id": "4j64881e-4d4e-4267-9314-fc89c012fcf2",
    "created_at": "2025-03-01T10:54:01.366304Z",
    "updated_at": "2025-03-01T10:54:01.366304Z",
}

mock_bar_prompt = {
    "name": "bar_prompt",
    "version": 5,
    "prompt": "hello {{products_added_to_cart}}, the count is {{total_clicks}}",
    "features": [
        {
            "name": "products_added_to_cart",
            "reference": "ecommerce_features:products_added_to_cart",
        },
        {"name": "total_clicks", "reference": "ecommerce_features:total_clicks"},
    ],
    "labels": ["production"],
    "tags": ["string"],
    "author": "string",
    "commit_msg": "",
    "id": "7e6e886e-4d4e-4267-9314-fc89c012fcf9",
    "created_at": "2025-03-01T12:54:01.366304Z",
    "updated_at": "2025-03-01T12:54:01.366304Z",
}


def get_prompt_response() -> dict[str, Any]:
    return mock_foo_prompt


def get_prompts_response() -> list[dict[str, Any]]:
    return [mock_foo_prompt, mock_bar_prompt]


def get_create_prompt_response() -> dict[str, Any]:
    return mock_foo_prompt_v2
