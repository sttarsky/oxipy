import importlib
import pkgutil

package = __package__

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{package}.{module_name}")
