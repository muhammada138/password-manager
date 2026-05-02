## 2024-05-24 - Cryptography structures lazy initialization
**Learning:** OmniVault employs a double-encryption architecture (file-level and entry-level). To prevent performance bottlenecks during bulk operations, cryptography structures that validate keys upon instantiation (like Fernet) should be lazily cached rather than re-instantiated per entry.
**Action:** Always check if cryptography primitives can be cached/reused if their keys don't change frequently to avoid initialization overhead.
