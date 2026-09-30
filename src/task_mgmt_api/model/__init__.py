from importlib import import_module
import pkgutil

for _, module_name, _ in pkgutil.iter_modules(__path__):
    import_module(f"{__name__}.{module_name}")
