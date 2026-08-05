from .criterion_wrapper import Criterion
from .model import Criteria as CriteriaInput


class Criteria(CriteriaInput):
    all: list[Criterion] | None = None
    any: list[Criterion] | None = None
