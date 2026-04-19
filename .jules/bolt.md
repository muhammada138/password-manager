## 2024-04-19 - O(N^2) sorting bottleneck in vault.py
**Learning:** Using `list.index(x)` inside a `sorted()` key function causes an O(N^2) complexity because `index()` itself is O(N).
**Action:** Always pre-compute a lookup dictionary mapping items to their indices to achieve O(1) lookups and keep sorting at O(N log N).
