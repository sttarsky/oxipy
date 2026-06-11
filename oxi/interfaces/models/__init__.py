import importlib
import pkgutil

package = __package__

for _, module_name, _ in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{package}.{module_name}")
