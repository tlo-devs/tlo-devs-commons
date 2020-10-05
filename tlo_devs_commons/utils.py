from uuid import UUID
from typing import Union
from pathlib import Path


def uuid4_is_valid(uuid: str) -> bool:
    try:
        val = UUID(uuid, version=4)
    except ValueError:
        return False
    return val.hex == uuid


class AttrDict(dict):
    __slots__ = []
    __doc__ = ""

    def __getattr__(self, item):
        return super(AttrDict, self).__getitem__(item)


class _TfvarsParser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> dict:
        with open(self.path, "r") as fin:
            c = fin.readlines()
        extract = lambda i: [el.strip() for el in [line.split("=")[i] for line in c]]
        keys = extract(0)
        vals = [line[1:-1] for line in extract(1)]
        kvpairs = {k: v for k, v in zip(keys, vals)}
        return kvpairs


class Tfvars:
    def __init__(self, /, path: Union[str, Path]) -> None:
        if not isinstance(path, Path):
            path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"The directory {path} does not exist")
        self.path = path
        self.vars = AttrDict(**_TfvarsParser(path).read())


__all__ = ["uuid4_is_valid", "Tfvars"]
