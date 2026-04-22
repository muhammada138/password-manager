## 2024-04-22 - Optimize Vault List Sorting
**Learning:** `list.index()` calls inside a `sorted()` key function cause O(N^2) time complexity, leading to severe performance bottlenecks when scaling items (e.g., thousands of applications in the vault).
**Action:** Always map lists to dictionaries for order-based sorting to ensure O(1) lookups during the sort, effectively bringing the operation down to O(N log N).
