from ..model import Criteria as _Criteria
from ..model import Criterion as _Criterion


class Criteria(_Criteria):
    def __and__(self, other):
        if isinstance(other, _Criterion):
            if self.all is not None:
                return Criteria(all=[*self.all, other], any=None)
        elif isinstance(other, _Criteria):
            if self.all is not None and other.all is not None:
                return Criteria(all=[*self.all, *other.all], any=None)
            elif self.all is not None and other.any is not None and len(other.any) == 1:
                return Criteria(all=[*self.all, *other.any], any=None)
            elif (
                self.any is not None
                and len(self.any) == 1
                and other.any is not None
                and len(other.any) == 1
            ):
                return Criteria(all=[*self.any, *other.any], any=None)
        return NotImplemented

    def __or__(self, other):
        if isinstance(other, _Criterion):
            if self.any is not None:
                return Criteria(all=None, any=[*self.any, other])
        elif isinstance(other, _Criteria):
            if self.any is not None and other.any is not None:
                return Criteria(all=None, any=[*self.any, *other.any])
            elif self.any is not None and other.all is not None and len(other.all) == 1:
                return Criteria(all=None, any=[*self.any, *other.all])
            elif (
                self.all is not None
                and len(self.all) == 1
                and other.all is not None
                and len(other.all) == 1
            ):
                return Criteria(all=None, any=[*self.all, *other.all])
        return NotImplemented


class Criterion(_Criterion):
    def __and__(self, other):
        if isinstance(other, _Criterion):
            return Criteria(all=[self, other], any=None)
        elif isinstance(other, _Criteria):
            if other.all is not None:
                return Criteria(all=[self, *other.all], any=None)
        return NotImplemented

    def __or__(self, other):
        if isinstance(other, _Criterion):
            return Criteria(all=None, any=[self, other])
        elif isinstance(other, _Criteria):
            if other.any is not None:
                return Criteria(all=None, any=[self, *other.any])
        return NotImplemented
