from abc import ABC, abstractmethod
from typing import Union
from sqlalchemy.inspection import inspect


class _IntrospectorInterface(ABC):
    def __init__(self, o__) -> None:
        self.schema = o__

    @abstractmethod
    def primary_keys(self) -> list:
        pass

    @abstractmethod
    def unique_keys(self) -> list:
        pass

    @abstractmethod
    def foreign_keys(self, columns_only: bool = False) -> Union[list, dict]:
        pass


class _declBaseIntrospector(_IntrospectorInterface):
    def primary_keys(self) -> list:
        return inspect(self.schema).primary_key

    def unique_keys(self) -> list:
        return [
            c.name for c in self.schema.__table__.columns if any(
                [c.primary_key, c.unique]
            )
        ]

    def foreign_keys(self, columns_only: bool = False) -> Union[list, dict]:
        foreign_keys = [c for c in self.schema.c if c.foreign_keys]
        fk_names = [key.name for key in foreign_keys]
        if columns_only:
            return fk_names
        fk_targets = [
            list(key.foreign_keys)[0].target_fullname for key in foreign_keys
        ]
        return {
            name: target for name, target in zip(fk_names, fk_targets)
        }


def SQLAIntrospector(o__):
    """
    Factory returning either a _declBaseIntrospector or _tblIntrospector
    """
    return _declBaseIntrospector(o__)


__all__ = ["SQLAIntrospector"]
