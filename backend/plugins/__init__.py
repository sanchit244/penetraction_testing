"""Plugin system for loading third-party scan modules.

The directory-based approach discovers any ``.py`` file inside the
``backend/plugins`` package that defines a callable ``run_scan`` function.
Each plugin must implement the following signature:

```python
def run_scan(target: str) -> dict:
    '''Execute the scan against *target* and return a result dict.

    The returned dictionary should contain at least "status" and
    "details" keys, but the exact schema is up to the caller.
    '''
    ...
```

The loader builds a registry mapping the plugin's module name (e.g.
``example_plugin``) to the callable.  The registry can be queried at
runtime via :func:`list_plugins` and :func:`get_plugin`.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from types import ModuleType
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

# Registry of plugin name -> callable
_plugin_registry: Dict[str, Callable[[str], dict]] = {}


def _load_plugin_module(module_name: str) -> ModuleType | None:
    """Import a module from the ``plugins`` package.

    Args:
        module_name: Name of the module without the package prefix.

    Returns:
        The imported module, or ``None`` if import fails.
    """
    full_name = f"plugins.{module_name}"
    try:
        module = importlib.import_module(full_name)
        logger.debug("Loaded plugin module %s", full_name)
        return module
    except Exception as exc:  # pragma: no cover – defensive
        logger.error("Failed to import plugin %s: %s", full_name, exc)
        return None


def _register_plugin(module: ModuleType) -> None:
    """Register a plugin if it defines a ``run_scan`` callable.

    The function must be named exactly ``run_scan`` and accept a single
    ``target`` argument.
    """
    plugin_name = module.__name__.split(".")[-1]
    run_scan = getattr(module, "run_scan", None)
    if callable(run_scan):
        _plugin_registry[plugin_name] = run_scan
        logger.info("Registered plugin '%s'", plugin_name)
    else:
        logger.warning(
            "Module %s does not expose a callable 'run_scan'; skipping.",
            module.__name__,
        )


def load_plugins() -> None:
    """Discover and load all plugins located in the ``plugins`` package.

    This function should be called once at application start‑up (e.g.
    in ``main.py`` before any scans are executed).
    """
    # ``pkgutil.iter_modules`` yields (module_finder, name, is_pkg)
    package = importlib.import_module("plugins")
    for _, mod_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if is_pkg:
            # Nested packages are not supported for the directory‑based style.
            logger.debug("Skipping subpackage %s in plugins directory", mod_name)
            continue
        module = _load_plugin_module(mod_name)
        if module:
            _register_plugin(module)


def list_plugins() -> List[str]:
    """Return a list of registered plugin names."""
    return list(_plugin_registry.keys())


def get_plugin(name: str) -> Callable[[str], dict] | None:
    """Retrieve a plugin's ``run_scan`` callable by name.

    Returns ``None`` if the plugin is not registered.
    """
    return _plugin_registry.get(name)

# Load plugins immediately when this package is imported.
load_plugins()
