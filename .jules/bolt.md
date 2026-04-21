## 2024-04-21 - O(n^2) list sorting overhead with list.index()
**Learning:** Using `list.index(x)` inside a sorting lambda creates an O(n^2 log n) bottleneck when sorting arrays based on dynamic, metadata-driven orderings.
**Action:** Always pre-compute a dictionary `order_idx = {item: i for i, item in enumerate(order)}` for O(1) lookups during sorting.
