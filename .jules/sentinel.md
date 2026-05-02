## 2024-05-24 - Fix SecureString Memory Leak

**Vulnerability:** `SecureString` was returning immutable `bytes` objects derived from `ctypes.create_string_buffer` when accessed via `get_bytes()`. Immutable bytes cannot be zeroed out safely in Python, causing sensitive passwords to remain in memory even after `SecureString` attempted to clear its buffer.

**Learning:** Memory meant to securely hold and subsequently zero-out secrets in Python MUST be backed by mutable data structures, like `bytearray`, rather than strings or raw `bytes`. This ensures that when the data is explicitly overwritten, the original memory location is actually zeroed out instead of creating a new object.

**Prevention:** Ensure that when building classes like `SecureString` designed to store sensitive data in memory and zero it later, a mutable structure like `bytearray` is used to hold the sensitive content from initialization. Ensure that any accessor methods return this mutable object.