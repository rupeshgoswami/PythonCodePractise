# Quant Developer Prep: Junior Level (Python, OOP, NumPy, pandas)

```
quant_junior/
├── section1_fundamentals.py   # collections, mutability, ==/is, slicing, *args/**kwargs,
│                              # comprehensions, exceptions, lambda/sorted, modules, files
├── section2_oop.py            # classes in depth: 4 pillars, BankAccount, Asset -> Stock,
│                              # @property, __str__/__repr__, super(), class/static methods
├── section3_numpy.py          # arrays, indexing, reshape, axis, boolean masks, rng, returns
├── section4_pandas.py         # Series/DataFrame, loc/iloc, filtering, NaN, pct_change, dates
├── quant_utils/               # tiny PACKAGE used by section 1 (modules vs packages)
│   ├── __init__.py
│   └── pricing.py
├── solutions.py               # reference solutions (open only after trying!)
└── run_all.py
```

## Setup
```bash
pip install numpy pandas
cd quant_junior
python section1_fundamentals.py      # run one section
python -c "import section1_fundamentals; section1_fundamentals.demo_collections()"      # run specific section.
python run_all.py                    # or everything
```
Always run from inside `quant_junior/` so `import quant_utils` works.

## How to study with this
1. Read a demo function top to bottom, predict the output, then run and compare with the `# ->` comments.
2. Change something (a slice, an axis, a class attribute) and re-run. Break it on purpose.
3. Retype the code from scratch in an empty file without looking: this is what fixes syntax in memory.
4. Each section ends with 3 exercises plus an automatic checker that prints `PASS` / `FAIL` / `not implemented yet`.
5. Only then compare with `solutions.py` (`python solutions.py` shows all PASS).

Tested on Python 3.12, NumPy 2.4, pandas 3.0 (also compatible with pandas 2.x).
