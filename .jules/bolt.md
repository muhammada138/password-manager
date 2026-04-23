## 2024-05-15 - Optimize list lookup in vault sorting logic
**Learning:** Using `list.index(x)` inside a sorting key function on a potentially large list results in O(N^2) complexity because `index()` itself is O(N) for each of the N elements sorted.
**Action:** Changed the logic in `get_accounts` and `get_apps` to pre-compute an index dictionary `order_idx = {x: i for i, x in enumerate(order)}`, allowing for O(1) lookups during the sort and reducing overall sorting complexity to O(N log N).
