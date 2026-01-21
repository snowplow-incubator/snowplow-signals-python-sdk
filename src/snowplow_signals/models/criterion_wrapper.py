from .model import (
    AtomicProperty,
    EntityProperty,
    EventProperty,
    SignalsApiModelsViewCriterionCriterion,
)


class Criterion(SignalsApiModelsViewCriterionCriterion):
    """Wrapper for the Criterion model from the Signals API."""

    @classmethod
    def eq(
        cls,
        property: AtomicProperty | EventProperty | EntityProperty,
        value: str | int | float | bool | list,
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property equals the value.

        Args:
            property: The property to check.
            value: The value to compare against.
        """
        return cls(property=property, operator="=", value=value)

    @classmethod
    def neq(
        cls,
        property: AtomicProperty | EventProperty | EntityProperty,
        value: str | int | float | bool | list,
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property does not equal the value.

        Args:
            property: The property to check.
            value: The value to compare against.
        """
        return cls(property=property, operator="!=", value=value)

    @classmethod
    def gt(
        cls,
        property: AtomicProperty | EventProperty | EntityProperty,
        value: int | float,
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property is greater than the value.

        Args:
            property: The property to check.
            value: The value to compare against.
        """
        return cls(property=property, operator=">", value=value)

    @classmethod
    def gte(
        cls,
        property: AtomicProperty | EventProperty | EntityProperty,
        value: int | float,
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property is greater than or equal to the value.

        Args:
            property: The property to check.
            value: The value to compare against.

        Returns:
            A Criterion instance.
        """
        return cls(property=property, operator=">=", value=value)

    @classmethod
    def lt(
        cls,
        property: AtomicProperty | EventProperty | EntityProperty,
        value: int | float,
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property is less than the value.

        Args:
            property: The property to check.
            value: The value to compare against.
        """
        return cls(property=property, operator="<", value=value)

    @classmethod
    def lte(
        cls,
        property: AtomicProperty | EventProperty | EntityProperty,
        value: int | float,
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property is less than or equal to the value.

        Args:
            property: The property to check.
            value: The value to compare against.
        """
        return cls(property=property, operator="<=", value=value)

    @classmethod
    def like(
        cls, property: AtomicProperty | EventProperty | EntityProperty, value: str
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property matches the value using a LIKE operator.

        Args:
            property: The property to check.
            value: The value to compare against.
        """
        return cls(property=property, operator="like", value=value)

    @classmethod
    def in_list(
        cls, property: AtomicProperty | EventProperty | EntityProperty, values: list
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property is in the list of values.

        Args:
            property: The property to check.
            values: The list of values to compare against.
        """
        return cls(property=property, operator="in", value=values)

    @classmethod
    def is_null(
        cls, property: AtomicProperty | EventProperty | EntityProperty
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property is null.

        Args:
            property: The property to check.

        Returns:
            A Criterion instance with 'is null' operator.
        """
        return cls(property=property, operator="is null", value=None)

    @classmethod
    def is_not_null(
        cls, property: AtomicProperty | EventProperty | EntityProperty
    ) -> "Criterion":
        """
        Creates a Criterion that checks if the property is not null.

        Args:
            property: The property to check.

        Returns:
            A Criterion instance with 'is not null' operator.
        """
        return cls(property=property, operator="is not null", value=None)
