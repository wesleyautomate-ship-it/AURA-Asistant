"""
Proxy package so `backend.app.*` imports resolve to the canonical `app.*`
modules without re-importing them under a second name.
"""

from importlib import abc, import_module, util
import sys
from types import ModuleType


class _AliasLoader(abc.Loader):
    def __init__(self, target: str):
        self._target = target

    def create_module(self, spec):
        return None

    def exec_module(self, module: ModuleType) -> None:
        target_module = import_module(self._target)
        module.__dict__.clear()
        module.__dict__.update(target_module.__dict__)
        module.__dict__["__loader__"] = self
        sys.modules[self._target] = target_module


class _AliasFinder(abc.MetaPathFinder):
    PREFIX = "backend.app"
    TARGET_PREFIX = "app"

    def find_spec(self, fullname, path, target=None):
        if fullname == self.PREFIX:
            target_name = self.TARGET_PREFIX
        elif fullname.startswith(self.PREFIX + "."):
            target_name = f"{self.TARGET_PREFIX}{fullname[len(self.PREFIX):]}"
        else:
            return None

        target_spec = util.find_spec(target_name)
        if target_spec is None:
            return None

        loader = _AliasLoader(target_name)
        spec = util.spec_from_loader(fullname, loader, origin=target_spec.origin)
        if target_spec.submodule_search_locations is not None:
            spec.submodule_search_locations = target_spec.submodule_search_locations
        return spec


if not any(isinstance(finder, _AliasFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())

sys.modules.setdefault("backend.app", import_module("app"))
