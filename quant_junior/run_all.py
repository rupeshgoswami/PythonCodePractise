"""Run every section in order:  python run_all.py"""
import section1_fundamentals as s1
import section2_oop as s2
import section3_numpy as s3
import section4_pandas as s4

if __name__ == "__main__":
    for mod in (s1, s2, s3, s4):
        print("\n\n" + "#" * 65 + f"\n# {mod.__name__}\n" + "#" * 65)
        # call every demo_* function in the order it was defined, then the checker
        for name, fn in vars(mod).items():
            if name.startswith("demo_") and callable(fn):
                fn()
        mod.check_exercises()
