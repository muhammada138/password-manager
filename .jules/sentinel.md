## 2024-04-22 - SecureString Memory Leak Fix
**Vulnerability:** In-memory sensitive data leakage. `IncrementalVault` stored the master password as a persistent plaintext string attribute. Additionally, `SecureString` leaked intermediate bytes objects into memory when calling `.encode()`.
**Learning:** Python's string `.encode('utf-8')` creates immutable `bytes` objects managed by the interpreter that cannot be deterministically zeroed out before garbage collection.
**Prevention:** Use a mutable `bytearray` encoded from the string, load it into a ctypes buffer using `from_buffer`, and explicitly zero out the `bytearray` (`b[i]=0`) before proceeding. Wrap passwords immediately in secure types and `.clear()` them as soon as derived keys are generated.
