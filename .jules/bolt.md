## 2024-05-24 - Optimize list sorting in vault

**Learning:** Using `list.index(x)` inside a sorting key function (e.g., `sorted(items, key=lambda x: order.index(x))`) results in O(n^2) time complexity because `index()` itself is O(n) and runs for each element during the sort.
**Action:** Always pre-compute a dictionary mapping elements to their indices before sorting (`order_idx = {name: i for i, name in enumerate(order)}`), changing the key lookup to O(1) and overall sorting to O(n log n).
