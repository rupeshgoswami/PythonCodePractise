"""
=====================================================================
SECTION 1: PYTHON FUNDAMENTALS  (Junior level, finance-themed)
=====================================================================
Run:  python section1_fundamentals.py

Each demo_xxx() function is self-contained. Read the comments, run it,
compare what prints with the "# ->" expected-output comments, then
change things and re-run. Breaking code on purpose is how you learn.
"""
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


# ---------------------------------------------------------------------
# 1.2  Mutable vs immutable
# ---------------------------------------------------------------------
def demo_mutability():
    header("1.2 Mutable vs immutable")
    # IMMUTABLE: int, float, str, tuple, frozenset, bool, None
    #   -> "changing" them creates a NEW object.
    # MUTABLE: list, dict, set, most custom objects
    #   -> can be changed in place; every name pointing at it sees the change.

    price = 100
    old_id = id(price)            # id() = identity (memory address in CPython)
    price += 1                    # builds a brand-new int 101 and rebinds `price`
    print("int: same object after +=?", id(price) == old_id)   # -> False

    positions = ["AAPL"]
    old_id = id(positions)
    positions += ["MSFT"]         # list += modifies the SAME list in place
    print("list: same object after +=?", id(positions) == old_id)  # -> True

    # Aliasing: two names, ONE list. A classic source of bugs.
    book_a = [100, 200]
    book_b = book_a               # NOT a copy, just another label
    book_b.append(300)
    print("book_a after changing book_b:", book_a)   # -> [100, 200, 300]
    book_c = book_a.copy()        # real (shallow) copy; also list(book_a) or book_a[:]
    book_c.append(999)
    print("book_a after changing copy :", book_a)    # -> [100, 200, 300]

    # Gotcha: mutable default arguments are created ONCE, at function definition.
    def add_trade_bad(trade, blotter=[]):
        blotter.append(trade)
        return blotter

    def add_trade_good(trade, blotter=None):     # the correct idiom
        if blotter is None:
            blotter = []
        blotter.append(trade)
        return blotter

    add_trade_bad("T1")
    print("bad default :", add_trade_bad("T2"))   # -> ['T1', 'T2']  (surprise!)
    add_trade_good("T1")
    print("good default:", add_trade_good("T2"))  # -> ['T2']

    # A tuple is immutable, but a list INSIDE it is still mutable.
    record = ("AAPL", [100, 200])
    record[1].append(300)
    print("tuple holding a list:", record)       # -> ('AAPL', [100, 200, 300])


# ---------------------------------------------------------------------
# 1.3  == vs is
# ---------------------------------------------------------------------
def demo_eq_vs_is():
    header("1.3 == vs is")
    # ==  compares VALUES   (calls __eq__)
    # is  compares IDENTITY (are these the very same object in memory?)
    a = [101.5, 102.0]
    b = [101.5, 102.0]
    c = a
    print("a == b:", a == b)   # -> True   same contents
    print("a is b:", a is b)   # -> False  two different list objects
    print("a is c:", a is c)   # -> True   c is just another name for a

    # Rule: use `is` ONLY for singletons: None, True, False.
    fill_price = None
    if fill_price is None:     # preferred over `== None`
        print("Order not filled yet")
    # Don't use `is` for numbers/strings: small-int/str caching makes it
    # *sometimes* True, which is an implementation detail, not a guarantee.


# ---------------------------------------------------------------------
# 1.4  Reversing: list.reverse() vs list[::-1]
# ---------------------------------------------------------------------
def demo_reverse():
    header("1.4 list.reverse() vs list[::-1]")
    prices = [100, 101, 102, 103]

    rev_copy = prices[::-1]    # NEW list, original untouched, O(n) extra memory
    print("slice copy:", rev_copy, "| original:", prices)   # -> [103, 102, 101, 100] | [100, 101, 102, 103]

    result = prices.reverse()  # IN PLACE, returns None, no extra list
    print("reverse() returned:", result, "| prices now:", prices)  # -> None | [103, 102, 101, 100]

    # reversed() gives a lazy iterator: good for looping without copying
    for p in reversed(prices):
        print(p, end=" ")      # -> 100 101 102 103
    print()


# ---------------------------------------------------------------------
# 1.5  Slicing a[start:stop:step]
# ---------------------------------------------------------------------
def demo_slicing():
    header("1.5 Slicing a[start:stop:step]")
    # start is INCLUDED, stop is EXCLUDED, step defaults to 1.
    # Missing start = beginning, missing stop = end. Negative = count from the end.
    p = [100, 101, 102, 103, 104, 105, 106, 107]
    #    0    1    2    3    4    5    6    7     (positive index)
    #   -8   -7   -6   -5   -4   -3   -2   -1    (negative index)
    print("p[2:5]   :", p[2:5])     # -> [102, 103, 104]
    print("p[:3]    :", p[:3])      # -> [100, 101, 102]  first 3 days
    print("p[-3:]   :", p[-3:])     # -> [105, 106, 107]  last 3 days
    print("p[::2]   :", p[::2])     # -> [100, 102, 104, 106] every 2nd day
    print("p[1::2]  :", p[1::2])    # -> [101, 103, 105, 107]
    print("p[::-1]  :", p[::-1])    # -> reversed
    print("p[5:1:-1]:", p[5:1:-1])  # -> [105, 104, 103, 102] backwards
    print("p[10:20] :", p[10:20])   # -> [] slicing never raises IndexError

    # Pairing "yesterday" with "today": the core trick behind daily returns
    rets = [(today - yest) / yest for yest, today in zip(p[:-1], p[1:])]
    print("returns  :", [round(r, 4) for r in rets[:3]])  # -> [0.01, 0.0099, 0.0098]

    # Slice ASSIGNMENT on lists (mutable)
    p[0:2] = [99, 99]
    print("after p[0:2]=[99,99]:", p[:4])  # -> [99, 99, 102, 103]
    print("works on strings too:", "AAPL.US"[:4])  # -> AAPL


# ---------------------------------------------------------------------
# 1.6  *args and **kwargs
# ---------------------------------------------------------------------
def total_notional(*trades):
    """*trades packs ANY number of positional args into a TUPLE."""
    print("   trades received as:", type(trades).__name__, trades)
    return sum(qty * px for qty, px in trades)


def place_order(ticker, qty, **options):
    """**options packs any extra keyword args into a DICT."""
    order_type = options.get("order_type", "MARKET")   # sensible defaults
    tif = options.get("tif", "DAY")
    return f"{qty} {ticker} {order_type} tif={tif} extras={options}"


def log_call(*args, **kwargs):
    """Accept anything: typical for wrappers/decorators (intermediate level)."""
    return f"args={args} kwargs={kwargs}"


def demo_args_kwargs():
    header("1.6 *args and **kwargs")
    print("total:", total_notional((100, 10.0), (50, 20.0)))   # -> 2000.0
    print(place_order("AAPL", 100))                     # -> 100 AAPL MARKET tif=DAY extras={}
    print(place_order("MSFT", 10, order_type="LIMIT", limit=405.0))
    # -> 10 MSFT LIMIT tif=DAY extras={'order_type': 'LIMIT', 'limit': 405.0}
    print(log_call(1, 2, side="BUY"))                  # -> args=(1, 2) kwargs={'side': 'BUY'}

    # The SAME stars UNPACK when calling a function:
    trade_list = [(10, 5.0), (20, 2.5)]
    print("unpacked list:", total_notional(*trade_list))   # same as total_notional((10,5.0),(20,2.5)) -> 100.0
    params = {"order_type": "STOP", "tif": "GTC"}
    print(place_order("TSLA", 5, **params))    # -> 5 TSLA STOP tif=GTC extras={...}

    # Star unpacking in assignment
    first, *middle, last = [100, 101, 102, 103]
    print("first, middle, last:", first, middle, last)   # -> 100 [101, 102] 103


# ---------------------------------------------------------------------
# 1.7  List comprehensions
# ---------------------------------------------------------------------
def demo_comprehensions():
    header("1.7 Comprehensions")
    # Pattern: [EXPRESSION for ITEM in ITERABLE if CONDITION]
    nums = range(10)
    squares_of_even = [n * n for n in nums if n % 2 == 0]
    print("squares of even:", squares_of_even)        # -> [0, 4, 16, 36, 64]

    # Equivalent loop (the comprehension is shorter and usually faster):
    out = []
    for n in nums:
        if n % 2 == 0:
            out.append(n * n)
    assert out == squares_of_even

    returns = [0.012, -0.004, 0.0, 0.021, -0.015]
    up_days = [r for r in returns if r > 0]                       # filter
    labels = ["UP" if r > 0 else "DOWN" if r < 0 else "FLAT" for r in returns]  # if/else goes BEFORE for
    print("up days:", up_days)   # -> [0.012, 0.021]
    print("labels :", labels)    # -> ['UP', 'DOWN', 'FLAT', 'UP', 'DOWN']

    tickers = ["aapl", "msft", "goog"]
    prices = [189.5, 410.2, 172.3]
    price_map = {t.upper(): p for t, p in zip(tickers, prices)}     # dict comprehension
    print("dict comp:", price_map)  # -> {'AAPL': 189.5, 'MSFT': 410.2, 'GOOG': 172.3}
    sectors = {s for s in ["Tech", "Energy", "Tech"]}               # set comprehension
    print("set comp :", sorted(sectors))   # -> ['Energy', 'Tech']

    # Nested: flatten a 2D list (read left to right like nested for-loops)
    matrix = [[1, 2], [3, 4], [5, 6]]
    print("flatten  :", [x for row in matrix for x in row])  # -> [1, 2, 3, 4, 5, 6]

    # Generator expression: ( ) instead of [ ] -> lazy, no list built in memory
    print("sum of squares:", sum(x * x for x in range(1_000)))   # -> 332833500


# ---------------------------------------------------------------------
# 1.8  append vs extend
# ---------------------------------------------------------------------
def demo_append_extend():
    header("1.8 append vs extend")
    a = [100, 101]
    a.append([102, 103])     # adds ONE element (here: the whole list as a single item)
    print("append:", a, "len", len(a))   # -> [100, 101, [102, 103]] len 3

    b = [100, 101]
    b.extend([102, 103])     # adds EACH element of the iterable
    print("extend:", b, "len", len(b))   # -> [100, 101, 102, 103] len 4

    c = [100]
    c.extend("AB")           # strings are iterable -> each char added!
    print("extend str:", c)  # -> [100, 'A', 'B']
    c.insert(0, 99)          # insert at a position (O(n), slower than append)
    print("insert:", c)      # -> [99, 100, 'A', 'B']


# ---------------------------------------------------------------------
# 1.9  Exception handling: try / except / else / finally
# ---------------------------------------------------------------------
class InvalidPriceError(ValueError):
    """Custom exception: subclass a built-in to give errors a domain meaning."""


def parse_price(raw):
    price = float(raw)            # may raise ValueError ("abc") or TypeError (None)
    if price <= 0:
        raise InvalidPriceError(f"price must be positive, got {price}")  # raise your own
    return price


def demo_exceptions():
    header("1.9 try / except / else / finally")
    for raw in ["101.25", "abc", "-5", None]:
        try:
            price = parse_price(raw)            # code that might fail
        except InvalidPriceError as e:          # most SPECIFIC first (it's a ValueError subclass)
            print(f"  {raw!r:>8}: business rule broken -> {e}")
        except (ValueError, TypeError) as e:    # catch several types in one clause
            print(f"  {raw!r:>8}: could not parse -> {type(e).__name__}")
        else:                                   # runs ONLY if no exception happened
            print(f"  {raw!r:>8}: parsed OK -> {price}")
        finally:                                # ALWAYS runs: cleanup (close files, DB, sockets)
            pass
    # -> '101.25': parsed OK -> 101.25
    # ->    'abc': could not parse -> ValueError
    # ->     '-5': business rule broken -> price must be positive, got -5.0
    # ->     None: could not parse -> TypeError

    # finally runs even if we return early
    def risky():
        try:
            return "returned from try"
        finally:
            print("  finally still ran")
    print(" ", risky())
    # Avoid bare `except:` -> it also swallows KeyboardInterrupt and hides bugs.


# ---------------------------------------------------------------------
# 1.10  lambda + sorted()
# ---------------------------------------------------------------------
def demo_lambda_sorted():
    header("1.10 lambda with sorted()")
    # lambda args: expression  -> a tiny anonymous function (single expression only)
    square = lambda x: x * x      # noqa: E731 (fine for learning, use def in real code)
    print("square(4):", square(4))   # -> 16

    trades = [("AAPL", 300), ("MSFT", 50), ("GOOG", 120)]   # (ticker, qty)
    by_qty = sorted(trades, key=lambda t: t[1])             # sort by SECOND element
    print("by qty asc :", by_qty)   # -> [('MSFT', 50), ('GOOG', 120), ('AAPL', 300)]
    print("by qty desc:", sorted(trades, key=lambda t: t[1], reverse=True))
    print("default    :", sorted(trades))   # tuples compare element by element -> by ticker

    # Multi-key: side ascending, then qty DESCENDING (negate numbers to flip)
    orders = [("SELL", 10), ("BUY", 5), ("BUY", 50), ("SELL", 70)]
    print("multi-key  :", sorted(orders, key=lambda o: (o[0], -o[1])))
    # -> [('BUY', 50), ('BUY', 5), ('SELL', 70), ('SELL', 10)]

    # sorted() returns a NEW list; list.sort() sorts IN PLACE and returns None
    trades.sort(key=lambda t: t[0])
    print("in-place by ticker:", trades)
    # key= also works with max/min
    print("biggest trade:", max(trades, key=lambda t: t[1]))   # -> ('AAPL', 300)


# ---------------------------------------------------------------------
# 1.11  Modules vs packages, if __name__ == "__main__"
# ---------------------------------------------------------------------
def demo_modules():
    header("1.11 Modules vs packages")
    import quant_utils                       # import the PACKAGE (runs its __init__.py)
    from quant_utils import pricing          # import a MODULE from the package
    from quant_utils.pricing import notional as ntl   # import one name, with alias

    print("simple_return:", quant_utils.simple_return(100, 105))   # -> 0.05
    print("notional     :", ntl(100, 189.5))                        # -> 18950.0
    print("pricing.__name__ when imported:", pricing.__name__)      # -> quant_utils.pricing
    print("this file's __name__          :", __name__)              # -> __main__ (when run directly)


# ---------------------------------------------------------------------
# 1.12  Files with `with open(...)`
# ---------------------------------------------------------------------
def demo_files():
    header("1.12 Reading / writing files")
    folder = tempfile.mkdtemp()                       # temp dir, so nothing pollutes your project
    path = os.path.join(folder, "trades.csv")         # os.path.join builds OS-correct paths

    # `with` = context manager: the file is closed automatically when the block
    # ends, EVEN IF an exception is raised. No forgotten f.close().
    # Modes: "r" read (default), "w" write (overwrites!), "a" append, "b" binary.
    with open(path, "w") as f:
        f.write("ticker,qty,price\n")
        f.write("AAPL,100,189.5\n")
        f.write("MSFT,50,410.2\n")

    with open(path, "a") as f:                        # append without erasing
        f.write("GOOG,20,172.3\n")

    total = 0.0
    with open(path) as f:
        header_line = next(f)                         # file objects are iterators: grab first line
        for line in f:                                # memory friendly, one line at a time
            ticker, qty, price = line.strip().split(",")
            total += int(qty) * float(price)
    print("header:", header_line.strip())             # -> ticker,qty,price
    print("total notional:", round(total, 2))         # -> 42906.0
    print("closed after with?", f.closed)             # -> True

    # JSON: the standard way to save dicts/lists as text
    jpath = os.path.join(folder, "positions.json")
    with open(jpath, "w") as f:
        json.dump({"AAPL": 100, "MSFT": 50}, f, indent=2)
    with open(jpath) as f:
        print("json loaded:", json.load(f))           # -> {'AAPL': 100, 'MSFT': 50}


# =====================================================================
# PRACTICE EXERCISES (Section 1). Fill in the bodies, then run this file.
# =====================================================================
def exercise_1_unique_tickers(trades):
    """
    Given a list of (ticker, qty) tuples, return a SORTED list of unique tickers
    whose total quantity is > 100.
    Example: [("AAPL", 60), ("MSFT", 10), ("AAPL", 50)] -> ["AAPL"]
    Hint: build a dict of totals, then a comprehension.
    """
    raise NotImplementedError


def exercise_2_safe_average(prices):
    """
    Return the average of the values in `prices` that can be converted to float.
    Skip bad entries using try/except. Return None if nothing is valid.
    Example: ["100", "x", "102", None] -> 101.0
    """
    raise NotImplementedError


def exercise_3_top_n(trades, n, **kwargs):
    """
    Return the n trades with the largest notional (qty * price), largest first.
    trades: list of (ticker, qty, price). If kwargs has side="SMALLEST",
    return the smallest n instead. Use sorted() with a lambda.
    """
    raise NotImplementedError


def check_exercises():
    header("Exercises")
    tests = [
        ("ex1", lambda: exercise_1_unique_tickers([("AAPL", 60), ("MSFT", 10), ("AAPL", 50)]) == ["AAPL"]),
        ("ex2", lambda: exercise_2_safe_average(["100", "x", "102", None]) == 101.0),
        ("ex3", lambda: exercise_3_top_n([("A", 1, 10), ("B", 5, 10), ("C", 2, 10)], 2)
                        == [("B", 5, 10), ("C", 2, 10)]),
    ]
    for name, test in tests:
        try:
            print(f"  {name}: {'PASS' if test() else 'FAIL'}")
        except NotImplementedError:
            print(f"  {name}: not implemented yet")


if __name__ == "__main__":
    demo_collections()
    demo_mutability()
    demo_eq_vs_is()
    demo_reverse()
    demo_slicing()
    demo_args_kwargs()
    demo_comprehensions()
    demo_append_extend()
    demo_exceptions()
    demo_lambda_sorted()
    demo_modules()
    demo_files()
    check_exercises()
