## 2024-04-25 - [Optimize sorting in get_apps and get_accounts]
**Learning:** Using `list.index()` inside a `sorted()` key function causes an O(n) operation inside an O(n log n) sorting algorithm, leading to O(n^2 log n) complexity.
**Action:** Pre-compute a dictionary mapping elements to their indices before sorting, enabling O(1) lookups during the sort and restoring O(n log n) performance.
