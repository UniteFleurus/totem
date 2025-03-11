
import copy
import os
import sys
from importlib import import_module
from importlib.util import find_spec as importlib_find


def autodiscover_modules(app_list, *module_to_import, prefix=None):
    """
    Auto-discover INSTALLED_APPS modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.

    """
    for app_name in app_list:
        for module_to_search in module_to_import:
            # Attempt to import the app's module.
            package_path = app_name
            if prefix:
                package_path = f"{prefix}.{package_path}"

            try:
                import_module(f"{package_path}.{module_to_search}")
            except Exception:
                # Decide whether to bubble up this error. If the app just
                # doesn't have the module in question, we can ignore the error
                # attempting to import it, otherwise we want it to bubble up.
                # If the imported package is erroneous, raise !
                if module_has_submodule(package_path, module_to_search):
                    raise

def module_has_submodule(package_name, module_name):
    try:
        spec = importlib_find("%s.%s" % (package_name, module_name))  # None or ModeSpec object. Or raise.
        return spec is not None
    except ImportError:
        return False
