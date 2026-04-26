## 2024-04-26 - [Sorting Metadata Lookups]
**Learning:** Using `list.index()` inside a `sorted()` key function causes `O(N^2 log N)` performance degradation when rendering UI lists.
**Action:** Always pre-compute an `O(1)` dictionary lookup (`{item: idx}`) before sorting based on custom order lists.
