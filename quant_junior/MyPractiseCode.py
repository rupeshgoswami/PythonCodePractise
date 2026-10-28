import json
import os
import tempfile


def header(title):
    """Small helper to print a visible section banner."""
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


# ---------------------------------------------------------------------
# 1.1  list, tuple, set, dict: differences and when to use each
# ---------------------------------------------------------------------
def demo_collections():
    header("1.1 list / tuple / set / dict")

    # LIST  [ ]  -> ordered, MUTABLE, duplicates allowed.
    # Use for: a sequence that grows/changes (prices arriving tick by tick).
    prices = [101.5, 102.0, 101.5, 103.2]
    prices.append(104.0)                 # mutate in place
    print("list :", prices)              # -> [101.5, 102.0, 101.5, 103.2, 104.0]
    print("first, last:", prices[0], prices[-1])  # -> 101.5 104.0

    # TUPLE ( ) -> ordered, IMMUTABLE, duplicates allowed.
    # Use for: a fixed record that must not change (a filled trade),
    # returning several values from a function, or as a dict key.
    trade = ("AAPL", 100, 189.5)         # (ticker, qty, price)
    ticker, qty, px = trade              # "tuple unpacking"
    print("tuple:", trade, "| unpacked:", ticker, qty, px)
    # trade[1] = 200  # TypeError: 'tuple' object does not support item assignment

    # SET { } -> UNORDERED, UNIQUE elements, very fast `in` checks (O(1)).
    # Use for: de-duplicating, membership tests, set algebra.
    traded = {"AAPL", "MSFT", "AAPL", "GOOG"}      # duplicate AAPL dropped
    print("set  :", sorted(traded))                # -> ['AAPL', 'GOOG', 'MSFT']
    print("'MSFT' in traded?", "MSFT" in traded)   # -> True
    watchlist = {"MSFT", "TSLA"}
    print("traded & watchlist:", traded & watchlist)          # -> {'MSFT'}
    print("traded | watchlist:", sorted(traded | watchlist))  # -> ['AAPL', 'GOOG', 'MSFT', 'TSLA']
    print("traded - watchlist:", sorted(traded - watchlist))  # -> ['AAPL', 'GOOG']
    empty_set = set()   # NOTE: {} is an empty DICT, not an empty set!

    # DICT {k: v} -> key -> value mapping, O(1) lookup, keeps insertion order (3.7+).
    # Keys must be immutable/hashable (str, int, tuple), values can be anything.
    # Use for: lookups by name (last price per ticker, positions per ticker).
    last_price = {"AAPL": 189.5, "MSFT": 410.2}
    last_price["GOOG"] = 172.3                     # add / overwrite
    print("dict :", last_price)
    print("TSLA price:", last_price.get("TSLA", "N/A"))  # .get avoids KeyError -> N/A
    for tkr, p in last_price.items():              # iterate key + value together
        print(f"   {tkr:<5} {p:>8.2f}")            # f-string: <5 left-align, >8.2f right, 2 dp

    # Tuple as dict key (lists can't be keys because they are mutable)
    fx = {("EUR", "USD"): 1.08, ("USD", "JPY"): 151.2}
    print("EURUSD:", fx[("EUR", "USD")])           # -> 1.08
    print("type of empty {}:", type({}).__name__, "| set():", type(empty_set).__name__)



if __name__ == "__main__":
    demo_collections()