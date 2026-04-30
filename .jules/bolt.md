## 2026-04-30 - Lazy caching Fernet object instances
**Learning:** OmniVault uses double-encryption (file-level + entry-level), which calls `Fernet()` repeatedly during entry saves/loads. Since `Fernet()` validates keys entirely in Python every time it's instantiated, this created significant overhead across multiple calls compared to actual encryption/decryption operations.
**Action:** Always cache instances of `Fernet()` (or similar costly-to-instantiate cryptography structures) to significantly improve repeated operation speeds.
