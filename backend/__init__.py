"""
Compatibility helpers for the backend package namespace.

The test suite sometimes imports modules using the `backend.app.*` prefix,
while the runtime code relies on the canonical `app.*` packages.  To avoid
double-importing modules (which can break SQLAlchemy metadata), we register a
meta-path finder that aliases `backend.app` imports to their `app` counterparts.
"""

from importlib import abc, import_module, util
import sys
from types import ModuleType


class _BackendAppAliasLoader(abc.Loader):
    """Loader that proxies module execution to the canonical `app.*` module."""

    def __init__(self, target_name: str):
        self._target_name = target_name

    def create_module(self, spec):
        # Defer to default module creation.
        return None

    def exec_module(self, module: ModuleType) -> None:
        target_module = import_module(self._target_name)
        module.__dict__.clear()
        module.__dict__.update(target_module.__dict__)
        module.__dict__["__loader__"] = self
        sys.modules[self._target_name] = target_module


class _BackendAppAliasFinder(abc.MetaPathFinder):
    """Meta path finder that maps `backend.app.*` to `app.*`."""

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

        loader = _BackendAppAliasLoader(target_name)
        spec = util.spec_from_loader(fullname, loader, origin=target_spec.origin)
        if target_spec.submodule_search_locations is not None:
            spec.submodule_search_locations = target_spec.submodule_search_locations
        return spec


if not any(isinstance(finder, _BackendAppAliasFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _BackendAppAliasFinder())

sys.modules.setdefault("backend.app", import_module("app"))
