"""
=====================================================================
SECTION 2: OOP / CLASSES  (Junior level, extra depth)
=====================================================================
Run:  python section2_oop.py

Roadmap for this file (each step builds on the previous one):
  2.1  class vs object
  2.2  self and __init__
  2.3  instance variables vs class variables
  2.4  ENCAPSULATION   -> BankAccount (deposit / withdraw / balance)
  2.5  ABSTRACTION     -> abstract base class Asset
  2.6  INHERITANCE     -> Stock(Asset), Bond(Asset), super()
  2.7  METHOD OVERRIDING
  2.8  POLYMORPHISM    -> one loop, many types
  2.9  @property (getter / setter / validation)
  2.10 __str__ vs __repr__ (+ a peek at __eq__, __len__)
  2.11 @classmethod vs @staticmethod
  2.12 Putting it together: a Portfolio (composition)
"""
from abc import ABC, abstractmethod


def header(title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


# =====================================================================
# 2.1  CLASS vs OBJECT
# =====================================================================
# A CLASS is a blueprint: it defines what data (attributes) and behaviour
# (methods) things of that kind have. An OBJECT (instance) is one concrete
# thing built from that blueprint, with its own data.
#   class  = the "Trade ticket" template
#   object = ticket #1 (AAPL, 100 @ 189.5), ticket #2 (MSFT, 50 @ 410.2), ...
class Trade:
    pass                 # an empty class is legal; `pass` = "nothing here yet"


def demo_class_vs_object():
    header("2.1 Class vs object")
    t1 = Trade()         # calling the class like a function CREATES an object
    t2 = Trade()
    t1.ticker = "AAPL"   # you *can* bolt attributes on, but __init__ (next) is the proper way
    print("type(t1):", type(t1).__name__)              # -> Trade
    print("isinstance(t1, Trade):", isinstance(t1, Trade))  # -> True
    print("t1 is t2:", t1 is t2)                       # -> False  (two separate objects)
    print("t1.ticker:", t1.ticker)                     # -> AAPL
    print("hasattr(t2, 'ticker'):", hasattr(t2, "ticker"))  # -> False (only t1 got it)
    print("Trade is itself an object of type:", type(Trade).__name__)  # -> type


# =====================================================================
# 2.2  self and __init__
# =====================================================================
class Order:
    # __init__ is the INITIALISER: Python calls it automatically right after
    # creating the object, so every Order starts in a valid, complete state.
    def __init__(self, ticker, qty, price, side="BUY"):
        # `self` is the object being built. self.x = ... stores data ON that object.
        # `self` is just a convention name, but always use it.
        self.ticker = ticker
        self.qty = qty
        self.price = price
        self.side = side

    # An instance method: first parameter is always self, so it can read the
    # object's own data.
    def notional(self):
        return self.qty * self.price

    def signed_qty(self):
        # Methods can call other attributes/methods through self
        return self.qty if self.side == "BUY" else -self.qty


def demo_self_init():
    header("2.2 self and __init__")
    o = Order("AAPL", 100, 189.5)          # Python does: Order.__init__(o, "AAPL", 100, 189.5)
    s = Order("MSFT", 50, 410.2, side="SELL")
    print("o.notional():", o.notional())   # -> 18950.0
    # Behind the scenes, o.notional() is exactly Order.notional(o):
    print("Order.notional(o):", Order.notional(o))   # -> 18950.0
    print("signed qty:", o.signed_qty(), s.signed_qty())   # -> 100 -50
    print("o.__dict__:", o.__dict__)       # every object stores its attributes in a dict
    # -> {'ticker': 'AAPL', 'qty': 100, 'price': 189.5, 'side': 'BUY'}


# =====================================================================
# 2.3  INSTANCE variables vs CLASS variables
# =====================================================================
class Equity:
    # CLASS variables: defined in the class body, SHARED by all instances.
    # Good for constants and counters that belong to the type, not one object.
    asset_class = "EQUITY"
    count = 0

    def __init__(self, ticker, exchange="NASDAQ"):
        # INSTANCE variables: defined on self, UNIQUE per object.
        self.ticker = ticker
        self.exchange = exchange
        Equity.count += 1        # update the CLASS variable via the class name


def demo_instance_vs_class_vars():
    header("2.3 Instance vs class variables")
    a = Equity("AAPL")
    b = Equity("SAP", exchange="XETRA")
    print("instance vars :", a.ticker, a.exchange, "|", b.ticker, b.exchange)
    print("class var via instance:", a.asset_class, b.asset_class)  # -> EQUITY EQUITY
    print("Equity.count:", Equity.count)                            # -> 2

    # Changing the class var on the CLASS affects everyone...
    Equity.asset_class = "STOCK"
    print("after Equity.asset_class='STOCK':", a.asset_class, b.asset_class)  # -> STOCK STOCK

    # ...but ASSIGNING through an instance creates a NEW instance var that
    # "shadows" the class var for that object only. Common interview trap.
    a.asset_class = "ADR"
    print("after a.asset_class='ADR':", a.asset_class, b.asset_class)  # -> ADR STOCK
    print("'asset_class' in a.__dict__:", "asset_class" in a.__dict__)  # -> True
    print("'asset_class' in b.__dict__:", "asset_class" in b.__dict__)  # -> False
    Equity.asset_class = "EQUITY"   # reset for later demos

    # Trap #2: a MUTABLE class variable is shared and mutated by everyone.
    class BadBook:
        trades = []                      # shared list!
        def add(self, t):
            self.trades.append(t)        # mutates the ONE shared list
    x, y = BadBook(), BadBook()
    x.add("T1")
    print("BadBook y.trades:", y.trades)  # -> ['T1']  y never added anything!
    # Fix: create the list in __init__ (self.trades = []).


# =====================================================================
# 2.4  ENCAPSULATION: BankAccount
# =====================================================================
# Encapsulation = bundle data + the methods that change it, and control
# access so the object can't get into an invalid state (e.g. negative balance).
# Python has no truly private fields; it uses NAMING CONVENTIONS:
#   name     -> public
#   _name    -> "internal, please don't touch" (convention only)
#   __name   -> name-mangled to _ClassName__name (harder to touch by accident)
class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""


class BankAccount:
    bank_name = "QuantBank"                  # class variable

    def __init__(self, owner, opening_balance=0.0):
        if opening_balance < 0:
            raise ValueError("opening balance cannot be negative")
        self.owner = owner                   # public
        self._balance = float(opening_balance)   # internal: change it ONLY via methods
        self._history = []                   # list created per instance (see 2.3 trap)
        self.__pin = "0000"                  # name-mangled "private"

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount
        self._history.append(("DEPOSIT", amount))
        return self._balance                 # returning the new balance is handy

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            raise InsufficientFundsError(
                f"cannot withdraw {amount:.2f}, balance is {self._balance:.2f}")
        self._balance -= amount
        self._history.append(("WITHDRAW", amount))
        return self._balance

    # @property turns a method into a READ-ONLY attribute: acct.balance (no parentheses).
    # There is no setter, so `acct.balance = 1e9` raises AttributeError. That's
    # encapsulation: the only ways to change money are deposit() and withdraw().
    @property
    def balance(self):
        return self._balance

    def statement(self):
        return list(self._history)           # return a COPY so callers can't edit our history


def demo_encapsulation_bank_account():
    header("2.4 Encapsulation: BankAccount")
    acct = BankAccount("Alice", 1_000)
    print("deposit 500 ->", acct.deposit(500))      # -> 1500.0
    print("withdraw 200 ->", acct.withdraw(200))    # -> 1300.0
    print("balance:", acct.balance)                 # -> 1300.0  (property, no ())

    try:
        acct.withdraw(5_000)
    except InsufficientFundsError as e:
        print("blocked:", e)            # -> cannot withdraw 5000.00, balance is 1300.00

    try:
        acct.balance = 1e9              # no setter defined
    except AttributeError as e:
        print("can't set balance directly:", type(e).__name__)   # -> AttributeError

    print("statement:", acct.statement())   # -> [('DEPOSIT', 500), ('WITHDRAW', 200)]
    # Name mangling in action:
    print("hasattr(acct, '__pin'):", hasattr(acct, "__pin"))                  # -> False
    print("hasattr(acct, '_BankAccount__pin'):", hasattr(acct, "_BankAccount__pin"))  # -> True


# =====================================================================
# 2.5  ABSTRACTION: abstract base class
# =====================================================================
# Abstraction = expose WHAT an object does, hide HOW. Callers just call
# asset.market_value(); they don't care if it's a stock, bond or option.
# An Abstract Base Class (ABC) defines a contract: "every Asset MUST
# implement market_value()". You can't instantiate the ABC itself.
class Asset(ABC):
    def __init__(self, symbol, quantity):
        self.symbol = symbol
        self.quantity = quantity

    @abstractmethod
    def market_value(self):
        """Every concrete asset must say how it is valued."""

    @abstractmethod
    def asset_type(self):
        ...

    # A CONCRETE method in the base class: inherited by every subclass for free.
    def describe(self):
        return f"{self.asset_type()} {self.symbol}: qty={self.quantity}, MV={self.market_value():,.2f}"


def demo_abstraction():
    header("2.5 Abstraction: abstract base class")
    try:
        Asset("X", 1)                    # abstract -> cannot be instantiated
    except TypeError as e:
        print("Asset('X', 1) ->", type(e).__name__, "(abstract methods not implemented)")

    class Incomplete(Asset):             # forgot to implement asset_type()
        def market_value(self):
            return 0
    try:
        Incomplete("Y", 1)
    except TypeError:
        print("Incomplete subclass also can't be instantiated -> contract enforced")


# =====================================================================
# 2.6  INHERITANCE: Stock and Bond inherit from Asset, using super()
# =====================================================================
# Inheritance = "is-a" relationship. A Stock IS an Asset, so it reuses
# Asset's code (describe, symbol, quantity) and adds/changes what's specific.
class Stock(Asset):
    def __init__(self, symbol, quantity, price, sector="Unknown"):
        # super() gives access to the PARENT class. Calling the parent's
        # __init__ sets symbol and quantity, so we don't duplicate that code.
        super().__init__(symbol, quantity)
        self.price = price               # extra attributes specific to Stock
        self.sector = sector

    def market_value(self):              # fulfils the abstract contract
        return self.quantity * self.price

    def asset_type(self):
        return "Stock"


class Bond(Asset):
    def __init__(self, symbol, quantity, face_value, clean_price_pct):
        super().__init__(symbol, quantity)
        self.face_value = face_value
        self.clean_price_pct = clean_price_pct    # bonds are quoted as % of face, e.g. 98.5

    def market_value(self):
        return self.quantity * self.face_value * self.clean_price_pct / 100

    def asset_type(self):
        return "Bond"


def demo_inheritance():
    header("2.6 Inheritance: Stock(Asset), Bond(Asset)")
    aapl = Stock("AAPL", 100, 189.5, sector="Tech")
    ust = Bond("UST10Y", 10, 1_000, 98.5)
    print(aapl.describe())    # describe() lives in Asset, inherited -> Stock AAPL: qty=100, MV=18,950.00
    print(ust.describe())     # -> Bond UST10Y: qty=10, MV=9,850.00
    print("isinstance(aapl, Asset):", isinstance(aapl, Asset))   # -> True  (a Stock IS an Asset)
    print("issubclass(Bond, Asset):", issubclass(Bond, Asset))   # -> True
    print("isinstance(aapl, Bond):", isinstance(aapl, Bond))     # -> False
    # MRO = Method Resolution Order: where Python looks for a method, in order.
    print("Stock MRO:", [c.__name__ for c in Stock.__mro__])   # -> ['Stock', 'Asset', 'ABC', 'object']


# =====================================================================
# 2.7  METHOD OVERRIDING (+ extending with super())
# =====================================================================
# Overriding = a subclass defines a method with the SAME NAME as the parent,
# replacing it. You can either REPLACE it fully, or EXTEND it by calling
# super().method() and adding to its result.
class DividendStock(Stock):
    def __init__(self, symbol, quantity, price, annual_dividend, sector="Unknown"):
        super().__init__(symbol, quantity, price, sector)   # reuse Stock's init (which reuses Asset's)
        self.annual_dividend = annual_dividend

    def asset_type(self):                    # REPLACE parent's version
        return "DividendStock"

    def describe(self):                      # EXTEND parent's version
        base = super().describe()            # run Asset.describe() first
        yld = self.annual_dividend / self.price
        return f"{base}, yield={yld:.2%}"    # :.2% formats 0.0256 as 2.56%


def demo_overriding():
    header("2.7 Method overriding")
    ko = DividendStock("KO", 200, 62.5, annual_dividend=1.94, sector="Staples")
    print(ko.describe())   # -> DividendStock KO: qty=200, MV=12,500.00, yield=3.10%
    print("MRO:", [c.__name__ for c in DividendStock.__mro__])
    # -> ['DividendStock', 'Stock', 'Asset', 'ABC', 'object']


# =====================================================================
# 2.8  POLYMORPHISM: same call, different behaviour
# =====================================================================
# Polymorphism = "many forms". Code written against the general type (Asset)
# works with ANY subclass. The loop below never checks the type; each object
# runs ITS OWN market_value(). Adding an Option class later needs zero
# changes to this loop. This is why OOP scales.
class Cash:
    """NOT an Asset subclass, but it has market_value() and describe()."""
    def __init__(self, amount):
        self.amount = amount

    def market_value(self):
        return self.amount

    def describe(self):
        return f"Cash: {self.amount:,.2f}"


def demo_polymorphism():
    header("2.8 Polymorphism")
    holdings = [
        Stock("AAPL", 100, 189.5),
        Bond("UST10Y", 10, 1_000, 98.5),
        DividendStock("KO", 200, 62.5, 1.94),
        Cash(5_000),          # DUCK TYPING: "if it quacks like a duck..." Python
    ]                         # only cares that the method exists, not the class.
    total = 0
    for h in holdings:
        print("  ", h.describe())
        total += h.market_value()     # one line, four different implementations
    print(f"Total MV: {total:,.2f}")   # -> 46,300.00

    # Built-in polymorphism you already use: + means different things per type
    print(1 + 2, "AA" + "PL", [1] + [2])   # -> 3 AAPL [1, 2]
    print("len works on many types:", len("AAPL"), len([1, 2]), len({"a": 1}))  # -> 4 2 1


# =====================================================================
# 2.9  @property with a SETTER (validation)
# =====================================================================
class Position:
    def __init__(self, symbol, quantity, avg_cost):
        self.symbol = symbol
        self.quantity = quantity        # goes THROUGH the setter below, so it's validated too
        self.avg_cost = avg_cost

    @property
    def quantity(self):                 # getter: runs on  pos.quantity
        return self._quantity

    @quantity.setter
    def quantity(self, value):          # setter: runs on  pos.quantity = value
        if not isinstance(value, int):
            raise TypeError("quantity must be an int")
        self._quantity = value

    @property
    def cost_basis(self):               # COMPUTED property: always up to date, never stale
        return self.quantity * self.avg_cost

    def pnl(self, market_price):
        return (market_price - self.avg_cost) * self.quantity


def demo_property():
    header("2.9 @property getter / setter")
    pos = Position("NVDA", 10, 120.0)
    print("cost basis:", pos.cost_basis)       # -> 1200.0
    pos.quantity = 15                          # calls the setter
    print("cost basis after qty=15:", pos.cost_basis)   # -> 1800.0  (recomputed automatically)
    print("PnL @ 130:", pos.pnl(130.0))        # -> 150.0
    try:
        pos.quantity = 2.5
    except TypeError as e:
        print("setter rejected 2.5:", e)       # -> quantity must be an int


# =====================================================================
# 2.10  __str__ vs __repr__  (+ a first look at other "dunder" methods)
# =====================================================================
# Dunder = "double underscore" methods. Python calls them for you:
#   print(obj) / str(obj) / f"{obj}"  -> __str__   (readable, for users)
#   repr(obj) / REPL / inside lists   -> __repr__  (unambiguous, for developers;
#                                                   ideally valid code to rebuild obj)
#   obj1 == obj2                      -> __eq__
#   len(obj)                          -> __len__
# If only __repr__ exists, str() falls back to it.
class Quote:
    def __init__(self, symbol, bid, ask):
        self.symbol, self.bid, self.ask = symbol, bid, ask   # multiple assignment

    @property
    def mid(self):
        return (self.bid + self.ask) / 2

    def __repr__(self):
        return f"Quote({self.symbol!r}, {self.bid}, {self.ask})"   # !r adds quotes to strings

    def __str__(self):
        return f"{self.symbol} {self.bid} / {self.ask} (mid {self.mid:.3f})"

    def __eq__(self, other):
        if not isinstance(other, Quote):
            return NotImplemented          # lets Python try other.__eq__ or fall back
        return (self.symbol, self.bid, self.ask) == (other.symbol, other.bid, other.ask)


class NoDunders:
    def __init__(self, x):
        self.x = x


def demo_str_repr():
    header("2.10 __str__ vs __repr__")
    q = Quote("EURUSD", 1.0841, 1.0843)
    print("print(q):", q)                      # -> EURUSD 1.0841 / 1.0843 (mid 1.084)
    print("repr(q) :", repr(q))                # -> Quote('EURUSD', 1.0841, 1.0843)
    print("in a list uses repr:", [q])         # -> [Quote('EURUSD', 1.0841, 1.0843)]
    print("q == copy:", q == Quote("EURUSD", 1.0841, 1.0843))   # -> True (values equal)
    print("q is copy:", q is Quote("EURUSD", 1.0841, 1.0843))   # -> False
    print("without dunders:", NoDunders(1))    # -> <__main__.NoDunders object at 0x...>


# =====================================================================
# 2.11  @classmethod vs @staticmethod
# =====================================================================
#   instance method  -> gets self  (the object)  : works with ONE object's data
#   @classmethod     -> gets cls   (the class)   : alternative constructors, class-level state
#   @staticmethod    -> gets nothing             : a plain helper function that logically
#                                                  belongs to the class
class Fill:
    _count = 0
    VALID_SIDES = ("BUY", "SELL")

    def __init__(self, symbol, qty, price, side):
        if not Fill.is_valid_side(side):
            raise ValueError(f"bad side {side!r}")
        self.symbol, self.qty, self.price, self.side = symbol, qty, price, side
        Fill._count += 1

    @classmethod
    def from_csv_line(cls, line):
        """Alternative constructor: build a Fill from 'AAPL,100,189.5,BUY'.
        Using cls (not Fill) means subclasses get back THEIR type."""
        symbol, qty, price, side = line.strip().split(",")
        return cls(symbol, int(qty), float(price), side)

    @classmethod
    def how_many(cls):
        return cls._count

    @staticmethod
    def is_valid_side(side):
        """No self, no cls: pure function, namespaced inside the class."""
        return side in Fill.VALID_SIDES

    def __repr__(self):
        return f"{type(self).__name__}({self.symbol!r}, {self.qty}, {self.price}, {self.side!r})"


class AlgoFill(Fill):
    pass


def demo_class_static_methods():
    header("2.11 @classmethod vs @staticmethod")
    f1 = Fill("AAPL", 100, 189.5, "BUY")
    f2 = Fill.from_csv_line("MSFT,50,410.2,SELL\n")
    f3 = AlgoFill.from_csv_line("GOOG,20,172.3,BUY")   # cls is AlgoFill here
    print(f1, f2, f3, sep="\n")
    # -> Fill('AAPL', 100, 189.5, 'BUY')
    # -> Fill('MSFT', 50, 410.2, 'SELL')
    # -> AlgoFill('GOOG', 20, 172.3, 'BUY')
    print("fills created:", Fill.how_many())          # -> 3
    print("is_valid_side('HOLD'):", Fill.is_valid_side("HOLD"))   # -> False
    try:
        Fill("TSLA", 1, 250.0, "HOLD")
    except ValueError as e:
        print("rejected:", e)                         # -> bad side 'HOLD'


# =====================================================================
# 2.12  PUTTING IT TOGETHER: Portfolio (composition)
# =====================================================================
# COMPOSITION = "has-a". A Portfolio HAS assets and HAS a cash account; it is
# not itself an Asset. Rule of thumb: prefer composition unless there is a
# clear "is-a" relationship.
class Portfolio:
    def __init__(self, name, cash_account):
        self.name = name
        self.cash = cash_account             # a BankAccount object lives inside
        self._holdings = {}                  # symbol -> Asset

    def buy_stock(self, symbol, qty, price):
        self.cash.withdraw(qty * price)      # reuse BankAccount's checks (may raise)
        if symbol in self._holdings:
            old = self._holdings[symbol]
            new_qty = old.quantity + qty
            avg = (old.market_value() + qty * price) / new_qty   # simple averaging
            self._holdings[symbol] = Stock(symbol, new_qty, avg)
        else:
            self._holdings[symbol] = Stock(symbol, qty, price)

    def add_asset(self, asset):
        if not isinstance(asset, Asset):
            raise TypeError("only Asset objects allowed")
        self._holdings[asset.symbol] = asset

    @property
    def total_value(self):
        return self.cash.balance + sum(a.market_value() for a in self._holdings.values())

    def weights(self):
        tv = self.total_value
        return {s: round(a.market_value() / tv, 4) for s, a in self._holdings.items()}

    def __len__(self):                       # len(portfolio) -> number of holdings
        return len(self._holdings)

    def __iter__(self):                      # `for asset in portfolio:` works
        return iter(self._holdings.values())

    def __repr__(self):
        return f"Portfolio({self.name!r}, holdings={len(self)}, value={self.total_value:,.2f})"


def demo_portfolio():
    header("2.12 Putting it together: Portfolio")
    pf = Portfolio("Growth", BankAccount("Fund", 100_000))
    pf.buy_stock("AAPL", 100, 189.5)     # cash 100,000 -> 81,050
    pf.buy_stock("MSFT", 50, 410.2)      # cash -> 60,540
    pf.add_asset(Bond("UST10Y", 20, 1_000, 98.5))   # transferred in, no cash spent
    print(pf)                            # -> Portfolio('Growth', holdings=3, value=119,700.00)
    print("cash left:", pf.cash.balance) # -> 60540.0
    print("weights  :", pf.weights())    # -> {'AAPL': 0.1583, 'MSFT': 0.1713, 'UST10Y': 0.1646}
    for asset in pf:                     # thanks to __iter__
        print("  ", asset.describe())
    try:
        pf.buy_stock("NVDA", 1_000, 120.0)   # 120,000 > cash
    except InsufficientFundsError as e:
        print("order rejected:", e)


# =====================================================================
# PRACTICE EXERCISES (Section 2)
# =====================================================================
# EX 1. SavingsAccount(BankAccount)
#   - Add an `interest_rate` instance variable (use super().__init__).
#   - Add method add_interest() that deposits balance * interest_rate.
#   - OVERRIDE withdraw() so that any single withdrawal > 1,000 raises ValueError,
#     otherwise call super().withdraw(amount).
#
# EX 2. Option(Asset)
#   - Attributes: symbol, quantity, strike, spot, is_call, multiplier=100.
#   - market_value() = intrinsic value * quantity * multiplier
#       call intrinsic = max(spot - strike, 0), put = max(strike - spot, 0)
#   - Add __repr__ and a @classmethod from_string("AAPL C 180 x3") or similar.
#   - Add it to the Portfolio in 2.12; confirm total_value updates WITHOUT
#     changing Portfolio code (that's polymorphism paying off).
#
# EX 3. Trade blotter
#   - Class TradeBlotter with a list of Fill objects (create the list in __init__!).
#   - Methods: add(fill), net_position(symbol) (BUY +qty, SELL -qty),
#     __len__, and a @property `symbols` returning a sorted list of unique symbols.

class SavingsAccount(BankAccount):
    pass   # EX 1: your code here


class Option(Asset):
    pass   # EX 2: your code here (remember: abstract methods must be implemented)


class TradeBlotter:
    pass   # EX 3: your code here


def check_exercises():
    header("Exercises")
    def ex1():
        s = SavingsAccount("Bob", 1_000, interest_rate=0.05)
        s.add_interest()
        ok = abs(s.balance - 1_050) < 1e-9
        try:
            s.withdraw(1_001)
            return False
        except ValueError:
            return ok
    def ex2():
        o = Option("AAPL", 2, strike=180, spot=190, is_call=True)
        return o.market_value() == 2_000
    def ex3():
        b = TradeBlotter()
        b.add(Fill("AAPL", 100, 1.0, "BUY"))
        b.add(Fill("AAPL", 30, 1.0, "SELL"))
        b.add(Fill("MSFT", 5, 1.0, "BUY"))
        return b.net_position("AAPL") == 70 and len(b) == 3 and b.symbols == ["AAPL", "MSFT"]
    for name, test in [("ex1", ex1), ("ex2", ex2), ("ex3", ex3)]:
        try:
            print(f"  {name}: {'PASS' if test() else 'FAIL'}")
        except Exception as e:   # broad on purpose: stubs fail in many ways
            print(f"  {name}: not done yet ({type(e).__name__})")


if __name__ == "__main__":
    demo_class_vs_object()
    demo_self_init()
    demo_instance_vs_class_vars()
    demo_encapsulation_bank_account()
    demo_abstraction()
    demo_inheritance()
    demo_overriding()
    demo_polymorphism()
    demo_property()
    demo_str_repr()
    demo_class_static_methods()
    demo_portfolio()
    check_exercises()
