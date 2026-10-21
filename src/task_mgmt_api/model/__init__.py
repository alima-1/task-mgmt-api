import pkgutil
from importlib import import_module

for _, module_name, _ in pkgutil.iter_modules(__path__):
    import_module(f"{__name__}.{module_name}")
