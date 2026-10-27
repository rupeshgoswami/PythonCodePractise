"""
=====================================================================
SECTION 3: NUMPY  (Junior level)
=====================================================================
Run:  python section3_numpy.py
Install if needed:  pip install numpy

NumPy's core object is the ndarray: an N-dimensional grid of values that
all share ONE dtype, stored in one contiguous block of memory.
"""
import time

import numpy as np   # `np` is the universal alias; always use it


def header(title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


# ---------------------------------------------------------------------
# 3.1  Why NumPy is faster than Python lists
# ---------------------------------------------------------------------
def demo_speed():
    header("3.1 Why NumPy is faster")
    # 1. CONTIGUOUS MEMORY + ONE DTYPE: a list stores pointers to separate
    #    Python objects scattered in memory; an array stores raw numbers
    #    side by side (8 bytes each for float64), which is CPU-cache friendly.
    # 2. VECTORISATION: the loop runs in compiled C, not in the Python
    #    interpreter, so there's no per-element type checking / dispatch.
    # 3. SIMD + BLAS: the CPU can process several numbers per instruction.
    n = 1_000_000
    py_list = list(range(n))
    arr = np.arange(n, dtype=np.float64)

    t0 = time.perf_counter()
    py_result = [x * 1.01 for x in py_list]      # Python-level loop
    t_list = time.perf_counter() - t0

    t0 = time.perf_counter()
    np_result = arr * 1.01                       # ONE vectorised C loop
    t_np = time.perf_counter() - t0

    print(f"list comprehension: {t_list*1000:7.2f} ms")
    print(f"numpy vectorised  : {t_np*1000:7.2f} ms  (~{t_list/t_np:.0f}x faster)")
    # Exact timings vary by machine; NumPy is typically 10-100x faster here.
    print("same answer?", np.allclose(py_result, np_result))   # -> True
    print("bytes per float64 element:", arr.itemsize)          # -> 8


# ---------------------------------------------------------------------
# 3.2  Creating arrays
# ---------------------------------------------------------------------
def demo_creation():
    header("3.2 Creating arrays")
    prices = np.array([100.0, 101.5, 99.8, 102.3])   # from a Python list
    print("np.array      :", prices)                  # -> [100.  101.5  99.8 102.3]
    print("np.zeros(3)   :", np.zeros(3))              # -> [0. 0. 0.]  e.g. init positions
    print("np.ones((2,3)):\n", np.ones((2, 3)))        # shape as a TUPLE for 2D
    print("np.arange(0,10,2):", np.arange(0, 10, 2))   # like range(): stop EXCLUDED -> [0 2 4 6 8]
    print("np.linspace(0,1,5):", np.linspace(0, 1, 5)) # N evenly spaced points, stop INCLUDED
    # -> [0.   0.25 0.5  0.75 1.  ]
    # arange = you choose the STEP; linspace = you choose the NUMBER of points
    # (linspace is safer with floats: arange(0, 1, 0.1) can surprise you with rounding).
    print("np.full(3, 0.5):", np.full(3, 0.5))         # -> [0.5 0.5 0.5]
    print("np.eye(2):\n", np.eye(2))                   # identity matrix
    print("int array:", np.array([1, 2, 3]), "| forced float:", np.array([1, 2, 3], dtype=float))


# ---------------------------------------------------------------------
# 3.3  shape, ndim, size, dtype
# ---------------------------------------------------------------------
def demo_attributes():
    header("3.3 shape / ndim / size / dtype")
    # 4 days (rows) x 3 stocks (columns): the classic price-matrix layout
    px = np.array([[100.0, 50.0, 20.0],
                   [101.0, 49.5, 20.4],
                   [102.5, 50.2, 20.1],
                   [101.8, 51.0, 20.8]])
    print("shape:", px.shape)    # -> (4, 3)   (rows, cols)
    print("ndim :", px.ndim)     # -> 2        number of dimensions/axes
    print("size :", px.size)     # -> 12       total element count = 4*3
    print("dtype:", px.dtype)    # -> float64
    qty = np.array([100, 200, 300])
    print("qty dtype:", qty.dtype)                     # -> int64 (on most systems)
    print("astype float32:", qty.astype(np.float32).dtype)   # astype returns a converted COPY
    print("mixed list -> upcast:", np.array([1, 2.5]).dtype) # -> float64 (one dtype for all)


# ---------------------------------------------------------------------
# 3.4  Indexing and slicing (1D and 2D)
# ---------------------------------------------------------------------
def demo_indexing():
    header("3.4 Indexing & slicing")
    p = np.array([100, 101, 102, 103, 104, 105])
    print("p[0], p[-1]:", p[0], p[-1])     # -> 100 105
    print("p[1:4]    :", p[1:4])           # -> [101 102 103]  same rules as lists
    print("p[::2]    :", p[::2])           # -> [100 102 104]
    print("p[[0,2,5]]:", p[[0, 2, 5]])     # "fancy indexing": pick by a list of positions -> [100 102 105]

    # 2D: arr[row, col]  (one bracket, comma-separated). Rows=days, cols=stocks.
    px = np.arange(1, 13).reshape(4, 3)
    print("px:\n", px)
    # [[ 1  2  3]
    #  [ 4  5  6]
    #  [ 7  8  9]
    #  [10 11 12]]
    print("px[1, 2]   :", px[1, 2])        # -> 6        row 1, col 2
    print("px[0]      :", px[0])           # -> [1 2 3]  first row (day 0, all stocks)
    print("px[:, 1]   :", px[:, 1])        # -> [ 2  5  8 11] column 1 (one stock, all days)
    print("px[-2:, :2]:\n", px[-2:, :2])   # last 2 rows, first 2 cols -> [[7 8] [10 11]]

    # IMPORTANT: a basic slice is a VIEW (shares memory), not a copy like with lists.
    col = px[:, 0]
    col[0] = 999
    print("after editing the slice, px[0,0] =", px[0, 0])   # -> 999 (original changed!)
    safe = px[:, 0].copy()     # use .copy() when you need independence
    # (Views vs copies are an intermediate topic; just remember .copy() for now.)


# ---------------------------------------------------------------------
# 3.5  reshape, flatten, ravel
# ---------------------------------------------------------------------
def demo_reshape():
    header("3.5 reshape / flatten / ravel")
    a = np.arange(6)                     # [0 1 2 3 4 5]
    m = a.reshape(2, 3)                  # same data, new shape; sizes must match (2*3 = 6)
    print("reshape(2,3):\n", m)
    print("reshape(3,-1):\n", a.reshape(3, -1))   # -1 = "work it out for me" -> (3, 2)
    print("as column (6,1) shape:", a.reshape(-1, 1).shape)   # -> (6, 1)
    # a.reshape(4, 2) -> ValueError: cannot reshape array of size 6 into shape (4,2)

    f = m.flatten()   # ALWAYS returns a new COPY (1D)
    r = m.ravel()     # returns a VIEW when possible (faster, no memory copy)
    f[0] = 100
    r[1] = 200
    print("flatten:", f, "| ravel:", r)
    print("m after editing both:\n", m)  # only ravel's change (200) shows up in m
    # -> [[  0 200   2]
    #     [  3   4   5]]
    print("transpose m.T shape:", m.T.shape)   # -> (3, 2)  rows <-> cols


# ---------------------------------------------------------------------
# 3.6  Element-wise operations
# ---------------------------------------------------------------------
def demo_elementwise():
    header("3.6 Element-wise operations")
    qty = np.array([100, 200, 50])
    price = np.array([189.5, 410.2, 172.3])
    print("qty * price:", qty * price)          # pairs elements: [18950. 82040.  8615.]
    print("price * 2  :", price * 2)            # scalar applied to every element
    print("price + 1  :", price + 1)
    print("price ** 2 :", np.round(price ** 2, 1))
    print("qty > 75   :", qty > 75)             # comparisons give BOOLEAN arrays -> [ True  True False]
    print("np.log     :", np.round(np.log(price), 4))   # "ufuncs": math on every element
    print("np.maximum :", np.maximum(price - 200, 0))   # element-wise max, e.g. call payoff
    print("dot product (portfolio value):", qty @ price)   # @ = matrix/dot product -> 109605.0
    # Shapes must match (or be "broadcastable", an intermediate topic):
    # np.array([1, 2]) + np.array([1, 2, 3]) -> ValueError


# ---------------------------------------------------------------------
# 3.7  sum, mean, std, min, max and the axis argument
# ---------------------------------------------------------------------
def demo_aggregations():
    header("3.7 Aggregations & axis")
    # rows = 3 days, cols = 2 stocks (AAPL, MSFT)
    rets = np.array([[0.01, 0.02],
                     [-0.02, 0.01],
                     [0.03, -0.01]])
    print("sum of all :", round(rets.sum(), 4))    # -> 0.04
    # axis=0 -> collapse the ROWS: one result PER COLUMN (per stock, down the days)
    # axis=1 -> collapse the COLUMNS: one result PER ROW (per day, across stocks)
    # Memory trick: the axis you pass is the axis that DISAPPEARS.
    print("mean axis=0 (per stock):", rets.mean(axis=0))    # -> [0.00666667 0.00666667]
    print("sum  axis=1 (per day)  :", rets.sum(axis=1))     # -> [ 0.03 -0.01  0.02]
    print("max per stock:", rets.max(axis=0), "| min per day:", rets.min(axis=1))
    print("argmax per stock (best day index):", rets.argmax(axis=0))   # -> [2 0]
    print("std  (ddof=0, population):", np.round(rets.std(axis=0), 5))
    print("std  (ddof=1, sample)    :", np.round(rets.std(axis=0, ddof=1), 5))
    # NumPy std defaults to ddof=0; pandas .std() defaults to ddof=1. Interview favourite!
    print("cumsum per stock:\n", rets.cumsum(axis=0))


# ---------------------------------------------------------------------
# 3.8  Boolean indexing
# ---------------------------------------------------------------------
def demo_boolean_indexing():
    header("3.8 Boolean indexing")
    rets = np.array([0.012, -0.004, 0.0, 0.021, -0.015, 0.007])
    mask = rets > 0                            # boolean array, same shape
    print("mask       :", mask)                # -> [ True False False  True False  True]
    print("rets[mask] :", rets[mask])          # -> [0.012 0.021 0.007]  only positives
    print("count up   :", mask.sum())          # True=1, False=0 -> 3
    print("hit ratio  :", mask.mean())         # fraction of up days -> 0.5
    # Combine conditions with & | ~ and PARENTHESES (not `and`/`or`):
    print("small moves:", rets[(rets > -0.01) & (rets < 0.01)])   # -> [-0.004  0.     0.007]
    print("big moves  :", rets[(rets > 0.01) | (rets < -0.01)])   # -> [ 0.012  0.021 -0.015]
    # np.where(cond, a, b): vectorised if/else
    print("signal     :", np.where(rets > 0, 1, -1))    # -> [ 1 -1 -1  1 -1  1]
    capped = rets.copy()
    capped[capped < -0.01] = -0.01             # assign through a mask (e.g. clip losses)
    print("capped     :", capped)


# ---------------------------------------------------------------------
# 3.9  Random numbers: np.random.default_rng
# ---------------------------------------------------------------------
def demo_random():
    header("3.9 Random numbers (default_rng)")
    # default_rng is the MODERN API (prefer it over the old np.random.seed / np.random.rand).
    # A seed makes results REPRODUCIBLE: same seed -> same numbers every run.
    rng = np.random.default_rng(seed=42)
    print("uniform [0,1):", np.round(rng.random(3), 4))     # -> [0.774  0.4389 0.8586]
    print("normal(0, 1%) :", np.round(rng.normal(loc=0.0, scale=0.01, size=3), 5))   # -> [ 0.00941 -0.01951 -0.01302]
    print("integers 1-6  :", rng.integers(1, 7, size=5))     # high is EXCLUSIVE -> [5 5 5 5 4]
    print("choice        :", rng.choice(["AAPL", "MSFT", "GOOG"], size=4))   # -> ['AAPL' 'GOOG' 'MSFT' 'MSFT']
    # (Each draw advances the generator, so these exact values need the same seed AND the same order of calls.)
    # Reproducibility check:
    a = np.random.default_rng(7).normal(size=3)
    b = np.random.default_rng(7).normal(size=3)
    print("same seed same numbers?", np.array_equal(a, b))   # -> True
    # 2D draws: 252 trading days x 3 stocks of daily returns
    sim = rng.normal(0.0005, 0.02, size=(252, 3))
    print("simulated returns shape:", sim.shape)             # -> (252, 3)
    print("sample mean per stock  :", np.round(sim.mean(axis=0), 5))   # -> [-6.0e-05 -3.0e-04 -1.2e-04]
    # True mean is 0.0005, yet all three samples are negative: with 2% daily noise,
    # one year of data barely tells you the drift. A key lesson for quant research.


# ---------------------------------------------------------------------
# 3.10  Daily returns from a price array
# ---------------------------------------------------------------------
def demo_daily_returns():
    header("3.10 Daily returns from prices")
    prices = np.array([100.0, 102.0, 99.96, 101.96, 104.0])

    # Method 1: slicing. "today" = prices[1:], "yesterday" = prices[:-1]
    simple = prices[1:] / prices[:-1] - 1
    print("simple returns:", np.round(simple, 4))   # -> [ 0.02 -0.02  0.02  0.02]
    # Note the result is ONE SHORTER than prices (no return on day 0).

    # Method 2: np.diff (p[t] - p[t-1])
    simple2 = np.diff(prices) / prices[:-1]
    print("same via diff :", np.allclose(simple, simple2))   # -> True

    # Log returns: additive over time, used a lot in quant models
    log_r = np.log(prices[1:] / prices[:-1])        # == np.diff(np.log(prices))
    print("log returns   :", np.round(log_r, 4))

    # Total return two ways (they must agree):
    total_from_prices = prices[-1] / prices[0] - 1
    total_compounded = np.prod(1 + simple) - 1      # compound the simple returns
    total_from_logs = np.exp(log_r.sum()) - 1       # sum the log returns
    print("total return  :", round(total_from_prices, 4), round(total_compounded, 4),
          round(total_from_logs, 4))                # -> 0.04 0.04 0.04

    # Annualised volatility (252 trading days a year)
    rng = np.random.default_rng(0)
    path = 100 * np.cumprod(1 + rng.normal(0.0004, 0.015, 252))   # synthetic 1-year price path
    r = path[1:] / path[:-1] - 1
    print("ann. vol      :", round(r.std(ddof=1) * np.sqrt(252), 4))   # ~ 0.015*sqrt(252) ~ 0.24

    # 2D: several stocks at once (rows=days, cols=stocks), same slicing along axis 0
    px = np.array([[100, 50], [101, 49], [103, 50]], dtype=float)
    print("2D returns:\n", np.round(px[1:] / px[:-1] - 1, 4))
    # -> [[ 0.01   -0.02  ]
    #     [ 0.0198  0.0204]]


# =====================================================================
# PRACTICE EXERCISES (Section 3)
# =====================================================================
def exercise_1_max_drawdown(prices):
    """
    Max drawdown = the worst peak-to-trough fall, as a negative fraction.
    prices [100, 120, 90, 130, 104] -> peak 120 to 90 = -0.25.
    Hint: running peak = np.maximum.accumulate(prices); drawdown = prices/peak - 1.
    No Python loops allowed!
    """
    raise NotImplementedError


def exercise_2_portfolio_returns(price_matrix, weights):
    """
    price_matrix: shape (days, stocks). weights: shape (stocks,), summing to 1.
    Return the 1D array of daily portfolio returns: (daily stock returns) @ weights.
    """
    raise NotImplementedError


def exercise_3_simulate_paths(s0, mu, sigma, days, n_paths, seed):
    """
    Return an array of shape (n_paths, days + 1) of simulated prices starting at s0,
    using daily returns ~ Normal(mu, sigma) from np.random.default_rng(seed).
    Column 0 must equal s0. Hint: np.cumprod(1 + returns, axis=1), then np.hstack/concatenate.
    """
    raise NotImplementedError


def check_exercises():
    header("Exercises")
    def ex1():
        return np.isclose(exercise_1_max_drawdown(np.array([100, 120, 90, 130, 104.0])), -0.25)
    def ex2():
        px = np.array([[100, 50], [110, 55.0]])
        return np.allclose(exercise_2_portfolio_returns(px, np.array([0.5, 0.5])), [0.1])
    def ex3():
        p = exercise_3_simulate_paths(100, 0.0, 0.01, 10, 5, seed=1)
        return p.shape == (5, 11) and np.all(p[:, 0] == 100)
    for name, test in [("ex1", ex1), ("ex2", ex2), ("ex3", ex3)]:
        try:
            print(f"  {name}: {'PASS' if test() else 'FAIL'}")
        except NotImplementedError:
            print(f"  {name}: not implemented yet")


if __name__ == "__main__":
    demo_speed()
    demo_creation()
    demo_attributes()
    demo_indexing()
    demo_reshape()
    demo_elementwise()
    demo_aggregations()
    demo_boolean_indexing()
    demo_random()
    demo_daily_returns()
    check_exercises()
