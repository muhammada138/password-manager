
## 2024-05-20 - O(N^2) Anti-Pattern in Python Sorting
**Learning:** Using `list.index(x)` inside the `key` lambda function for Python's `sorted()` function results in an $O(N^2 \log N)$ worst-case time complexity because `index()` is an $O(N)$ lookup operation called for each element.
**Action:** Always convert the ordered list into a hash map (dictionary) where the keys are the list items and values are their indices (`{item: i for i, item in enumerate(order)}`). Use `.get()` on this hash map inside the sort key to achieve $O(1)$ lookups, bringing the overall sort time down to $O(N \log N)$.
