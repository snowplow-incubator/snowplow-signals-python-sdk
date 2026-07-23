from .criterion_wrapper import Criterion  # noqa: F401
from .model import Criteria as CriteriaModel


class Criteria(CriteriaModel):
    all: list[Criterion] | None = None  # type: ignore[override]
    any: list[Criterion] | None = None  # type: ignore[override]
