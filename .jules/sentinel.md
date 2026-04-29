## 2024-04-29 - Secure Upgrade of Cryptographic Parameters
**Vulnerability:** The vault used 200,000 PBKDF2 iterations, which is lower than the recommended 600,000 for modern security standards.
**Learning:** Upgrading cryptographic parameters (like iterations) requires a backward-compatible fallback mechanism in the decryption process (`load()`) to prevent data loss for existing users.
**Prevention:** Always implement graceful fallbacks to legacy parameters when increasing security standards, allowing seamless access to older data.
