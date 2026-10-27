"""
pricing.py is a MODULE (one .py file) living inside the quant_utils PACKAGE.
"""


def simple_return(p_old: float, p_new: float) -> float:
    """Return (p_new - p_old) / p_old, e.g. 100 -> 105 gives 0.05."""
    return (p_new - p_old) / p_old


def notional(qty: int, price: float) -> float:
    """Trade value = quantity * price."""
    return qty * price


# __name__ is a special variable Python sets for every module:
#   - "__main__"            when you run the file directly:  python quant_utils/pricing.py
#   - "quant_utils.pricing" when another file imports it
# So the block below runs ONLY when executed directly, never on import.
# Use it for quick self-tests / demos that shouldn't fire when others import you.
if __name__ == "__main__":
    print("Running pricing.py directly, __name__ =", __name__)
    print(simple_return(100, 105))  # 0.05
