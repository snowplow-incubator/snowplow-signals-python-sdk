from __future__ import annotations

import json
import pprint
import re  # noqa: F401
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Set

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictStr,
    field_validator,
)
from typing_extensions import Annotated, Self


class EntityIdentifiers(BaseModel):
    """
    EntityIdentifiers
    """  # noqa: E501

    session: Optional[List[Any]] = None
    user: Optional[List[Any]] = None
    __properties: ClassVar[List[str]] = ["session", "user"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of EntityIdentifiers from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if session (nullable) is None
        # and model_fields_set contains the field
        if self.session is None and "session" in self.model_fields_set:
            _dict["session"] = None

        # set to None if user (nullable) is None
        # and model_fields_set contains the field
        if self.user is None and "user" in self.model_fields_set:
            _dict["user"] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EntityIdentifiers from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {"session": obj.get("session"), "user": obj.get("user")}
        )
        return _obj


class FeatureRef(BaseModel):
    """
    FeatureRef
    """  # noqa: E501

    name: Annotated[str, Field(min_length=1, strict=True, max_length=128)] = Field(
        description="The name of a feature in the prompt to be replaced. Will be inside double curly brackets in the prompt."
    )
    reference: StrictStr = Field(
        description="The reference of the feature stored in the online store. Format is {feature_view}:{feature_name}."
    )
    __properties: ClassVar[List[str]] = ["name", "reference"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of FeatureRef from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FeatureRef from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {"name": obj.get("name"), "reference": obj.get("reference")}
        )
        return _obj


class PromptBase(BaseModel):
    """
    PromptBase
    """  # noqa: E501

    name: Annotated[str, Field(min_length=1, strict=True, max_length=128)] = Field(
        description="The name of the prompt, given by the user. Also used by the SDK as reference to fetch a prompt."
    )
    version: Annotated[int, Field(strict=True, ge=1)] = Field(
        description="The version of the prompt, incremented automatically when updating the prompt."
    )
    prompt: Annotated[str, Field(min_length=1, strict=True)] = Field(
        description="The contents of the prompt, written by the user."
    )
    features: List[FeatureRef] = Field(
        description="The features the prompt references by name."
    )
    labels: List[StrictStr] = Field(
        description="A list of labels that are only added by the system. E.g. 'production', 'latest'"
    )
    tags: List[StrictStr] = Field(
        description="A list of tags to categorize the prompt."
    )
    author: StrictStr = Field(description="The author of the prompt.")
    commit_msg: Optional[StrictStr]
    __properties: ClassVar[List[str]] = [
        "name",
        "version",
        "prompt",
        "features",
        "labels",
        "tags",
        "author",
        "commit_msg",
    ]

    @field_validator("name")
    def name_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[A-Za-z0-9_]+$", value):
            raise ValueError(r"must validate the regular expression /^[A-Za-z0-9_]+$/")
        return value

    @field_validator("labels")
    def labels_validate_enum(cls, value):
        """Validates the enum"""
        for i in value:
            if i not in set(["production", "latest"]):
                raise ValueError(
                    "each list item must be one of ('production', 'latest')"
                )
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of PromptBase from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in features (list)
        _items = []
        if self.features:
            for _item_features in self.features:
                if _item_features:
                    _items.append(_item_features.to_dict())
            _dict["features"] = _items
        # set to None if commit_msg (nullable) is None
        # and model_fields_set contains the field
        if self.commit_msg is None and "commit_msg" in self.model_fields_set:
            _dict["commit_msg"] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PromptBase from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "name": obj.get("name"),
                "version": obj.get("version"),
                "prompt": obj.get("prompt"),
                "features": (
                    [FeatureRef.from_dict(_item) for _item in obj["features"]]
                    if obj.get("features") is not None
                    else None
                ),
                "labels": obj.get("labels"),
                "tags": obj.get("tags"),
                "author": obj.get("author"),
                "commit_msg": obj.get("commit_msg"),
            }
        )
        return _obj


class PromptDeletedResponse(BaseModel):
    """
    PromptDeletedResponse
    """  # noqa: E501

    ok: StrictBool
    __properties: ClassVar[List[str]] = ["ok"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of PromptDeletedResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PromptDeletedResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({"ok": obj.get("ok")})
        return _obj


class PromptResponse(BaseModel):
    """
    PromptResponse
    """  # noqa: E501

    name: Annotated[str, Field(min_length=1, strict=True, max_length=128)] = Field(
        description="The name of the prompt, given by the user. Also used by the SDK as reference to fetch a prompt."
    )
    version: Annotated[int, Field(strict=True, ge=1)] = Field(
        description="The version of the prompt, incremented automatically when updating the prompt."
    )
    prompt: Annotated[str, Field(min_length=1, strict=True)] = Field(
        description="The contents of the prompt, written by the user."
    )
    features: List[FeatureRef] = Field(
        description="The features the prompt references by name."
    )
    labels: List[StrictStr] = Field(
        description="A list of labels that are only added by the system. E.g. 'production', 'latest'"
    )
    tags: List[StrictStr] = Field(
        description="A list of tags to categorize the prompt."
    )
    author: StrictStr = Field(description="The author of the prompt.")
    commit_msg: Optional[StrictStr]
    id: StrictStr
    created_at: datetime
    updated_at: datetime
    __properties: ClassVar[List[str]] = [
        "name",
        "version",
        "prompt",
        "features",
        "labels",
        "tags",
        "author",
        "commit_msg",
        "id",
        "created_at",
        "updated_at",
    ]

    @field_validator("name")
    def name_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[A-Za-z0-9_]+$", value):
            raise ValueError(r"must validate the regular expression /^[A-Za-z0-9_]+$/")
        return value

    @field_validator("labels")
    def labels_validate_enum(cls, value):
        """Validates the enum"""
        for i in value:
            if i not in set(["production", "latest"]):
                raise ValueError(
                    "each list item must be one of ('production', 'latest')"
                )
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of PromptResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in features (list)
        _items = []
        if self.features:
            for _item_features in self.features:
                if _item_features:
                    _items.append(_item_features.to_dict())
            _dict["features"] = _items
        # set to None if commit_msg (nullable) is None
        # and model_fields_set contains the field
        if self.commit_msg is None and "commit_msg" in self.model_fields_set:
            _dict["commit_msg"] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PromptResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "name": obj.get("name"),
                "version": obj.get("version"),
                "prompt": obj.get("prompt"),
                "features": (
                    [FeatureRef.from_dict(_item) for _item in obj["features"]]
                    if obj.get("features") is not None
                    else None
                ),
                "labels": obj.get("labels"),
                "tags": obj.get("tags"),
                "author": obj.get("author"),
                "commit_msg": obj.get("commit_msg"),
                "id": obj.get("id"),
                "created_at": obj.get("created_at"),
                "updated_at": obj.get("updated_at"),
            }
        )
        return _obj


class PromptHydrateResponse(BaseModel):
    """
    PromptHydrateResponse
    """  # noqa: E501

    prompt: StrictStr
    __properties: ClassVar[List[str]] = ["prompt"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of PromptHydrateResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PromptHydrateResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({"prompt": obj.get("prompt")})
        return _obj
