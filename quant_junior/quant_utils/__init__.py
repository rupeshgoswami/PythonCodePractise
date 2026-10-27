"""
quant_utils is a PACKAGE: a folder of modules, marked by this __init__.py file.

- A MODULE is a single .py file (e.g. pricing.py).
- A PACKAGE is a directory that groups related modules (e.g. quant_utils/).

Code in __init__.py runs once, the first time the package is imported.
Re-exporting names here lets users write `from quant_utils import simple_return`
instead of `from quant_utils.pricing import simple_return`.
"""
from .pricing import simple_return, notional  # relative import: "." = this package

__all__ = ["simple_return", "notional"]  # what `from quant_utils import *` exposes
