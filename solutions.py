"""
REFERENCE SOLUTIONS. Try every exercise yourself BEFORE opening this file!

Run:  python solutions.py
It plugs these solutions into each section's checker, so every line should say PASS.
"""
import io

import numpy as np
import pandas as pd

import section1_fundamentals as s1
import section2_oop as s2
import section3_numpy as s3
import section4_pandas as s4


# ----------------------------- Section 1 -----------------------------
def unique_tickers(trades):
    totals = {}
    for ticker, qty in trades:
        totals[ticker] = totals.get(ticker, 0) + qty
    return sorted(t for t, q in totals.items() if q > 100)


def safe_average(prices):
    valid = []
    for p in prices:
        try:
            valid.append(float(p))
        except (TypeError, ValueError):
            continue
    return sum(valid) / len(valid) if valid else None


def top_n(trades, n, **kwargs):
    smallest = kwargs.get("side") == "SMALLEST"
    return sorted(trades, key=lambda t: t[1] * t[2], reverse=not smallest)[:n]


# ----------------------------- Section 2 -----------------------------
class SavingsAccount(s2.BankAccount):
    def __init__(self, owner, opening_balance=0.0, interest_rate=0.0):
        super().__init__(owner, opening_balance)
        self.interest_rate = interest_rate

    def add_interest(self):
        return self.deposit(self.balance * self.interest_rate)

    def withdraw(self, amount):
        if amount > 1_000:
            raise ValueError("single withdrawal limit is 1,000")
        return super().withdraw(amount)


class Option(s2.Asset):
    def __init__(self, symbol, quantity, strike, spot, is_call=True, multiplier=100):
        super().__init__(symbol, quantity)
        self.strike, self.spot, self.is_call, self.multiplier = strike, spot, is_call, multiplier

    @property
    def intrinsic(self):
        diff = self.spot - self.strike if self.is_call else self.strike - self.spot
        return max(diff, 0)

    def market_value(self):
        return self.intrinsic * self.quantity * self.multiplier

    def asset_type(self):
        return "Call" if self.is_call else "Put"

    @classmethod
    def from_string(cls, text, spot):
        """'AAPL C 180 x3' -> 3 AAPL 180 calls."""
        symbol, cp, strike, qty = text.split()
        return cls(symbol, int(qty.lstrip("x")), float(strike), spot, is_call=(cp == "C"))

    def __repr__(self):
        return f"Option({self.symbol!r}, {self.quantity}, {self.strike}, {self.spot}, is_call={self.is_call})"


class TradeBlotter:
    def __init__(self):
        self._fills = []

    def add(self, fill):
        self._fills.append(fill)

    def net_position(self, symbol):
        return sum(f.qty if f.side == "BUY" else -f.qty for f in self._fills if f.symbol == symbol)

    def __len__(self):
        return len(self._fills)

    @property
    def symbols(self):
        return sorted({f.symbol for f in self._fills})


# ----------------------------- Section 3 -----------------------------
def max_drawdown(prices):
    peak = np.maximum.accumulate(prices)
    return (prices / peak - 1).min()


def portfolio_returns(price_matrix, weights):
    rets = price_matrix[1:] / price_matrix[:-1] - 1
    return rets @ weights


def simulate_paths(s0, mu, sigma, days, n_paths, seed):
    rng = np.random.default_rng(seed)
    rets = rng.normal(mu, sigma, size=(n_paths, days))
    growth = np.cumprod(1 + rets, axis=1)
    return s0 * np.hstack([np.ones((n_paths, 1)), growth])


# ----------------------------- Section 4 -----------------------------
def big_buys(trades):
    df = trades.assign(notional=trades["qty"] * trades["price"])
    df = df[(df["side"] == "BUY") & (df["notional"] > 20_000)]
    return (df.sort_values("notional", ascending=False)[["trade_id", "ticker", "notional"]]
              .reset_index(drop=True))


def clean_returns(prices):
    return prices.ffill().pct_change().dropna()


def from_csv(csv_text):
    df = pd.read_csv(io.StringIO(csv_text))
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df["ticker"].value_counts().to_dict()


if __name__ == "__main__":
    # Patch the solutions into each module, then reuse the module's own checker.
    s1.exercise_1_unique_tickers, s1.exercise_2_safe_average, s1.exercise_3_top_n = \
        unique_tickers, safe_average, top_n
    s2.SavingsAccount, s2.Option, s2.TradeBlotter = SavingsAccount, Option, TradeBlotter
    s3.exercise_1_max_drawdown, s3.exercise_2_portfolio_returns, s3.exercise_3_simulate_paths = \
        max_drawdown, portfolio_returns, simulate_paths
    s4.exercise_1_big_buys, s4.exercise_2_clean_returns, s4.exercise_3_from_csv = \
        big_buys, clean_returns, from_csv

    for mod in (s1, s2, s3, s4):
        print(f"\n### {mod.__name__}", end="")
        mod.check_exercises()

    # Bonus from Section 2, EX 2: the Portfolio picks up the Option with no code changes
    pf = s2.Portfolio("Demo", s2.BankAccount("Fund", 10_000))
    pf.add_asset(Option.from_string("AAPL C 180 x3", spot=190))
    print("\nPortfolio with an option:", pf)   # -> value=13,000.00 (10,000 cash + 3,000 option)
