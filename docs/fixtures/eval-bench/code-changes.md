# Code Changes Eval Fixture

Local diff summary:

- `src/coupon.py` adds a branch for `coupon.amount > order_total`.
- `tests/test_coupon.py` has no coverage for the new branch yet.
- Risk is medium because checkout pricing can affect payment correctness.
