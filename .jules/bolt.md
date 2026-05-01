## 2024-05-01 - Cache Cryptography Objects
**Learning:** Cryptography structures like `Fernet` inherently validate keys upon instantiation. In a double-encryption architecture processing bulk read/writes (`get_entry` / `set_entry`), re-instantiating these objects per operation creates a significant O(N) performance bottleneck.
**Action:** Always lazily cache initialized cryptographic primitives (like `Fernet`) at the class level instead of dynamically re-instantiating them inside frequently called loop/bulk operation methods.
