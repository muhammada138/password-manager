## 2024-04-20 - [List Sorting Optimization]
**Learning:** O(n^2) time complexity caused by O(n) lookups via `list.index(x)` inside the O(n log n) `sorted()` key function limits sorting performance on larger datasets.
**Action:** Use an index dictionary created with `enumerate(order)` to achieve O(1) lookups in `sorted()` key function, maintaining overall O(n log n) performance.
