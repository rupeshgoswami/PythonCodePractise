"""
=====================================================================
SECTION 4: PANDAS  (Junior level)
=====================================================================
Run:  python section4_pandas.py
Install if needed:  pip install pandas numpy
Works with pandas 2.x and 3.x.

pandas = labelled NumPy. A Series is a 1D array with an INDEX (labels);
a DataFrame is a table of Series sharing the same index (one per column).
"""
import io
import os
import tempfile

import numpy as np
import pandas as pd   # `pd` is the universal alias

pd.set_option("display.width", 120)          # print wide tables on one line
pd.set_option("display.max_columns", 20)


def header(title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


def make_trades():
    """Synthetic trade blotter used by several demos. Fresh copy each call."""
    return pd.DataFrame({
        "trade_id": [1, 2, 3, 4, 5, 6, 7, 8],
        "date":     ["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03",
                     "2024-01-04", "2024-01-04", "2024-01-05", "2024-01-05"],
        "ticker":   ["AAPL", "MSFT", "AAPL", "GOOG", "MSFT", "AAPL", "GOOG", "MSFT"],
        "side":     ["BUY", "BUY", "SELL", "BUY", "SELL", "BUY", "SELL", "BUY"],
        "qty":      [100, 50, 40, 200, 30, 150, 120, 80],
        "price":    [185.6, 370.9, 184.2, 138.9, 368.0, 181.9, 140.3, 367.8],
    })


# ---------------------------------------------------------------------
# 4.1  Series vs DataFrame
# ---------------------------------------------------------------------
def demo_series_vs_dataframe():
    header("4.1 Series vs DataFrame")
    # SERIES: 1D values + index labels. Like a dict and a NumPy array combined.
    last = pd.Series([189.5, 410.2, 172.3], index=["AAPL", "MSFT", "GOOG"], name="last_px")
    print(last)
    # AAPL    189.5
    # MSFT    410.2
    # GOOG    172.3
    # Name: last_px, dtype: float64
    print("by label  :", last["MSFT"])       # -> 410.2
    print("vectorised:", (last * 2).tolist())  # element-wise like NumPy -> [379.0, 820.4, 344.6]
    print(".values is a NumPy array:", type(last.to_numpy()).__name__)   # -> ndarray

    # Series arithmetic ALIGNS ON LABELS, not position:
    qty = pd.Series({"GOOG": 10, "AAPL": 5})   # different order, MSFT missing
    print("qty * last (aligned):\n", qty * last)
    # AAPL    947.5
    # GOOG   1723.0
    # MSFT      NaN   <- no MSFT in qty, so NaN (missing)

    # DATAFRAME: 2D table. Each column is a Series; all share one index.
    df = pd.DataFrame({"last_px": last, "sector": ["Tech", "Tech", "Comm"]})
    print(df)
    print("df['last_px'] is a", type(df["last_px"]).__name__)     # -> Series   (single brackets)
    print("df[['last_px']] is a", type(df[["last_px"]]).__name__) # -> DataFrame (list of columns)


# ---------------------------------------------------------------------
# 4.2  Creating / reading data and inspecting it
# ---------------------------------------------------------------------
def demo_create_and_inspect():
    header("4.2 Creating, reading, inspecting")
    # (a) from a dict of lists (column-oriented): most common
    trades = make_trades()
    # (b) from a list of dicts (row-oriented): e.g. JSON from an API
    rows = [{"ticker": "AAPL", "qty": 10}, {"ticker": "MSFT", "qty": 5}]
    print("from list of dicts:\n", pd.DataFrame(rows))
    # (c) from a NumPy array + column names
    arr = np.random.default_rng(1).normal(0, 0.01, size=(3, 2))
    print("from numpy:\n", pd.DataFrame(arr, columns=["AAPL", "MSFT"]).round(4))

    # (d) READ CSV. io.StringIO makes a string behave like a file, so no real file is
    #     needed. With a real file you'd write pd.read_csv("trades.csv").
    csv_text = """ticker,qty,price
AAPL,100,185.6
MSFT,50,370.9
GOOG,200,138.9
"""
    from_csv = pd.read_csv(io.StringIO(csv_text))
    print("read_csv:\n", from_csv)

    # Round trip through a real temp file: to_csv / read_csv
    path = os.path.join(tempfile.mkdtemp(), "trades.csv")
    trades.to_csv(path, index=False)          # index=False: don't write the 0..n-1 row labels
    back = pd.read_csv(path)
    print("round trip equal?", back.equals(trades))   # -> True

    # INSPECTING: the first things to do with ANY new dataset
    print("\nhead(3):\n", trades.head(3))     # first n rows (default 5); tail(n) = last n
    print("\nshape:", trades.shape)           # -> (8, 6)  (rows, cols); attribute, no ()
    print("columns:", list(trades.columns))
    print("dtypes:\n", trades.dtypes)         # note: 'date' is text, NOT datetime yet (fixed in 4.10)
    print("\ninfo():")
    trades.info()                             # columns, non-null counts, dtypes, memory. Prints itself.
    print("\ndescribe():\n", trades.describe().round(2))  # stats for numeric cols
    print("\ndescribe text cols:\n", trades.describe(exclude="number"))   # count/unique/top/freq


# ---------------------------------------------------------------------
# 4.3  Selecting rows/columns: loc vs iloc
# ---------------------------------------------------------------------
def demo_loc_iloc():
    header("4.3 loc vs iloc")
    # loc  -> by LABEL    (index labels, column names). Slices INCLUDE the end.
    # iloc -> by POSITION (integers 0..n-1, like NumPy). Slices EXCLUDE the end.
    # Both take [rows, cols].
    df = make_trades().set_index("trade_id")   # index labels are now 1..8, not 0..7
    print("columns:")
    print(" df['qty'].tolist():", df["qty"].tolist())      # one column -> Series
    print(" df[['ticker','qty']] shape:", df[["ticker", "qty"]].shape)   # -> (8, 2)

    print("\nloc[3] (label 3):\n", df.loc[3])              # the row whose LABEL is 3
    print("\niloc[3] (4th row) ticker:", df.iloc[3]["ticker"])   # position 3 = label 4 -> GOOG

    print("\nloc[2:4, ['ticker','qty']]  (labels 2,3,4: END INCLUDED):")
    print(df.loc[2:4, ["ticker", "qty"]])
    print("\niloc[1:4, 1:3]  (positions 1,2,3: END EXCLUDED):")
    print(df.iloc[1:4, 1:3])

    print("\nsingle value loc[5,'price']:", df.loc[5, "price"])   # -> 368.0
    print("single value iloc[0, -1]   :", df.iloc[0, -1])         # first row, last col -> 185.6
    print("last 2 rows via iloc:\n", df.iloc[-2:])

    # Setting values: ALWAYS use .loc[row, col] = value (one step).
    # df[df.qty > 100]["price"] = 0  <- "chained assignment": does NOT modify df.
    df.loc[1, "price"] = 186.0
    print("after df.loc[1,'price']=186:", df.loc[1, "price"])     # -> 186.0


# ---------------------------------------------------------------------
# 4.4  Filtering rows with conditions
# ---------------------------------------------------------------------
def demo_filtering():
    header("4.4 Filtering")
    df = make_trades()
    big = df[df["qty"] > 100]          # boolean mask, exactly like NumPy
    print("qty > 100:\n", big)
    # -> trade_ids 4 (GOOG 200), 6 (AAPL 150), 7 (GOOG 120)

    # Combine with & | ~ and PARENTHESES around each condition:
    print("\nBUY and qty>=80:\n", df[(df["side"] == "BUY") & (df["qty"] >= 80)])
    print("\nNOT AAPL count:", (~(df["ticker"] == "AAPL")).sum())   # -> 5
    print("\nisin AAPL/GOOG ids:", df.loc[df["ticker"].isin(["AAPL", "GOOG"]), "trade_id"].tolist())
    # -> [1, 3, 4, 6, 7]
    # .query(): string syntax, often more readable
    print("\nquery:\n", df.query("ticker == 'MSFT' and price > 368"))
    # filter rows AND pick columns at once with loc:
    print("\nloc mask + cols:\n", df.loc[df["qty"] > 100, ["ticker", "qty"]])


# ---------------------------------------------------------------------
# 4.5  Adding, renaming, dropping columns
# ---------------------------------------------------------------------
def demo_columns():
    header("4.5 Add / rename / drop columns")
    df = make_trades()
    df["notional"] = df["qty"] * df["price"]                  # new column from vectorised maths
    df["signed_qty"] = np.where(df["side"] == "BUY", df["qty"], -df["qty"])  # if/else per row
    df["venue"] = "NASDAQ"                                    # scalar broadcast to all rows
    df = df.assign(fee=lambda d: d["notional"] * 0.0001)      # assign(): returns a NEW df (chainable)
    print(df.head(3).round(2))

    df = df.rename(columns={"qty": "quantity", "price": "px"})   # returns a new df
    print("\nrenamed:", list(df.columns))

    df = df.drop(columns=["venue", "fee"])                       # drop columns
    df = df.drop(index=[0, 1])                                   # drop rows by index label
    print("after drop:", list(df.columns), "| rows:", len(df))  # rows -> 6
    print("net signed qty per ticker:", df.groupby("ticker")["signed_qty"].sum().to_dict())
    # -> {'AAPL': 110, 'GOOG': 80, 'MSFT': 50}  (groupby is intermediate; just a preview)


# ---------------------------------------------------------------------
# 4.6  Sorting
# ---------------------------------------------------------------------
def demo_sorting():
    header("4.6 Sorting")
    df = make_trades()
    print("by qty desc:\n", df.sort_values("qty", ascending=False).head(3))
    # -> trade_ids 4 (200), 6 (150), 7 (120)
    print("\nby ticker asc, then qty desc:")
    print(df.sort_values(["ticker", "qty"], ascending=[True, False])[["ticker", "qty"]])
    print("\nnlargest(2, 'price'):\n", df.nlargest(2, "price")[["ticker", "price"]])  # shortcut for top-N
    shuffled = df.sample(frac=1, random_state=0)       # shuffle rows reproducibly
    print("\nsort_index restores order:", shuffled.sort_index().index.tolist())  # -> [0..7]


# ---------------------------------------------------------------------
# 4.7  Missing values: isna, dropna, fillna
# ---------------------------------------------------------------------
def demo_missing():
    header("4.7 Missing values")
    px = pd.DataFrame({
        "AAPL": [185.6, np.nan, 184.2, 181.9, np.nan],   # np.nan = "missing" for floats
        "MSFT": [370.9, 368.0, np.nan, 367.8, 371.2],
    }, index=pd.date_range("2024-01-01", periods=5, freq="D"))
    print(px)
    print("\nisna():\n", px.isna())
    print("\nmissing per column:", px.isna().sum().to_dict())   # -> {'AAPL': 2, 'MSFT': 1}
    print("any missing at all?", px.isna().any().any())        # -> True

    print("\ndropna() (any NaN in row -> drop):\n", px.dropna())          # 2 rows survive
    print("\ndropna(subset=['MSFT']) rows:", len(px.dropna(subset=["MSFT"])))  # -> 4
    print("\nfillna(0):\n", px.fillna(0))   # usually WRONG for prices: price 0 is a fake crash
    print("\nffill() (carry last known price forward, standard for prices):\n", px.ffill())
    print("\nfillna with column means:\n", px.fillna(px.mean()).round(2))
    # None of these change px in place; they return new DataFrames. Assign the result.


# ---------------------------------------------------------------------
# 4.8  Daily returns with pct_change()
# ---------------------------------------------------------------------
def demo_pct_change():
    header("4.8 Daily returns with pct_change()")
    px = pd.DataFrame({
        "AAPL": [100.0, 102.0, 99.96, 101.96],
        "MSFT": [400.0, 404.0, 408.04, 404.0],
    }, index=pd.date_range("2024-01-02", periods=4, freq="B"))   # "B" = business days
    rets = px.pct_change()            # (today / yesterday) - 1, per column
    print(rets.round(4))
    #             AAPL    MSFT
    # 2024-01-02   NaN     NaN    <- first row has no "yesterday"
    # 2024-01-03  0.02  0.0100
    # 2024-01-04 -0.02  0.0100
    # 2024-01-05  0.02 -0.0099
    rets = rets.dropna()
    print("\nmean daily return:", rets.mean().round(4).to_dict())   # -> {'AAPL': 0.0067, 'MSFT': 0.0034}
    print("cumulative return:", ((1 + rets).prod() - 1).round(4).to_dict())  # -> AAPL 0.0196, MSFT 0.01
    print("same from prices :", (px.iloc[-1] / px.iloc[0] - 1).round(4).to_dict())
    print("log returns:\n", np.log(px / px.shift(1)).dropna().round(4))   # shift(1) = yesterday's row
    print("ann. vol (pandas std uses ddof=1):", (rets.std() * np.sqrt(252)).round(4).to_dict())
    # -> {'AAPL': 0.3666, 'MSFT': 0.1824}


# ---------------------------------------------------------------------
# 4.9  value_counts()
# ---------------------------------------------------------------------
def demo_value_counts():
    header("4.9 value_counts()")
    df = make_trades()
    print(df["ticker"].value_counts())   # sorted by count, descending
    # AAPL    3
    # MSFT    3
    # GOOG    2
    print("\nshare of trades by side:\n", df["side"].value_counts(normalize=True))   # BUY 0.625, SELL 0.375
    print("\nticker/side combos:\n", df[["ticker", "side"]].value_counts())
    print("\nunique tickers:", df["ticker"].nunique(), sorted(df["ticker"].unique()))   # -> 3


# ---------------------------------------------------------------------
# 4.10  Datetime column -> index
# ---------------------------------------------------------------------
def demo_datetime_index():
    header("4.10 to_datetime + set_index")
    df = make_trades()
    print("before:", df["date"].dtype)                 # text: 'object' in pandas 2.x, 'str' in 3.x
    df["date"] = pd.to_datetime(df["date"])            # parse strings to Timestamps
    print("after :", df["date"].dtype)                 # -> datetime64[ns] (2.x) / datetime64[us] (3.x)
    # .dt accessor: date parts, like .str for strings
    print("weekday names:", df["date"].dt.day_name().unique().tolist())
    # -> ['Tuesday', 'Wednesday', 'Thursday', 'Friday']

    df = df.set_index("date")                          # dates become the row labels
    print(df.head(3))
    print("\nindex type:", type(df.index).__name__)    # -> DatetimeIndex
    # Now you can slice by date strings (end INCLUDED, as with all loc label slices):
    print("\nrows on 2024-01-03 .. 2024-01-04:\n", df.loc["2024-01-03":"2024-01-04", ["ticker", "qty"]])
    print("\nall January 2024 rows:", len(df.loc["2024-01"]))   # partial-string indexing -> 8
    df = df.sort_index()                               # keep a time index sorted
    print("is sorted:", df.index.is_monotonic_increasing)   # -> True
    # reset_index() undoes set_index (date goes back to being a column)
    print("columns after reset_index:", list(df.reset_index().columns)[:3])  # -> ['date', 'trade_id', 'ticker']


# =====================================================================
# PRACTICE EXERCISES (Section 4)
# =====================================================================
def exercise_1_big_buys(trades):
    """
    From make_trades(): add a 'notional' column and return ONLY BUY trades with
    notional > 20,000, sorted by notional descending, with columns
    ['trade_id', 'ticker', 'notional'] and a fresh 0..n-1 index (reset_index(drop=True)).
    Expected trade_ids in order: [8, 4, 6]
    """
    raise NotImplementedError


def exercise_2_clean_returns(prices):
    """
    prices: DataFrame of prices with a DatetimeIndex, may contain NaN.
    Forward-fill missing prices, compute daily returns with pct_change(),
    drop the first (NaN) row and return the result.
    """
    raise NotImplementedError


def exercise_3_from_csv(csv_text):
    """
    csv_text has columns date,ticker,close (dates as strings, unsorted).
    Read it with pd.read_csv(io.StringIO(csv_text)), convert 'date' to datetime,
    set it as index, sort by index, and return the number of rows per ticker
    as a dict, e.g. {'AAPL': 2, 'MSFT': 1}.
    """
    raise NotImplementedError


def check_exercises():
    header("Exercises")
    def ex1():
        out = exercise_1_big_buys(make_trades())
        return out["trade_id"].tolist() == [8, 4, 6] and list(out.columns) == ["trade_id", "ticker", "notional"]
    def ex2():
        p = pd.DataFrame({"A": [100, np.nan, 110.0]}, index=pd.date_range("2024-01-01", periods=3))
        r = exercise_2_clean_returns(p)
        return len(r) == 2 and np.allclose(r["A"].to_numpy(), [0.0, 0.1])
    def ex3():
        txt = "date,ticker,close\n2024-01-03,AAPL,1\n2024-01-02,MSFT,2\n2024-01-02,AAPL,3\n"
        return exercise_3_from_csv(txt) == {"AAPL": 2, "MSFT": 1}
    for name, test in [("ex1", ex1), ("ex2", ex2), ("ex3", ex3)]:
        try:
            print(f"  {name}: {'PASS' if test() else 'FAIL'}")
        except NotImplementedError:
            print(f"  {name}: not implemented yet")


if __name__ == "__main__":
    demo_series_vs_dataframe()
    demo_create_and_inspect()
    demo_loc_iloc()
    demo_filtering()
    demo_columns()
    demo_sorting()
    demo_missing()
    demo_pct_change()
    demo_value_counts()
    demo_datetime_index()
    check_exercises()
