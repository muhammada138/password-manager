## 2024-05-24 - [Optimize sorting in get_apps and get_accounts]
**Learning:** Using `list.index(x)` inside a `sorted()` key function causes O(N^2) complexity because `index()` itself takes O(N) time and runs for each element during the O(N log N) sort.
**Action:** Always pre-compute a dictionary mapping elements to their indices (`order_idx = {k: i for i, k in enumerate(order)}`) to ensure O(1) lookups during sorting.
