from .criterion_wrapper import Criterion
from .model import CriteriaInput


class Criteria(CriteriaInput):
    all: list[Criterion] | None = None
    any: list[Criterion] | None = None
