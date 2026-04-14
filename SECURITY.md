# Security Architecture

This document details the security architecture and cryptographic implementations of the Password Manager. Our primary goal is to ensure the confidentiality, integrity, and availability of user data, both at rest and during execution.

## 1. Cryptography

### Key Derivation
The master password is never stored directly. Instead, a strong key derivation function is used to generate the necessary encryption and authentication keys:
- **Algorithm:** PBKDF2HMAC
- **Hash Function:** SHA-256
- **Iterations:** 200,000
- **Derived Key Length:** 64 bytes total

### Split-Key Architecture
The 64 bytes derived from the master password are split into two independent 32-byte keys to separate encryption from authentication:
1.  **Encryption Key:** The first 32 bytes are base64-urlsafe encoded to generate the `Fernet` encryption key.
2.  **Authentication Key:** The remaining 32 bytes serve as an independent `HMAC-SHA256` key for integrity verification.

### Encryption & Integrity Layer (Encrypt-then-MAC)
To protect against chosen-ciphertext attacks and ensure data integrity, the application implements an Encrypt-then-MAC approach:
-   **Encryption:** Data is encrypted using `Fernet` (AES-128-CBC with a random IV and PKCS7 padding).
-   **Authentication:** An `HMAC-SHA256` tag is computed over the `Fernet` ciphertext using the independent Authentication Key and appended to the final output.
-   **Verification:** During decryption, `hmac.compare_digest` is used to evaluate the HMAC tag against the ciphertext in constant time *before* any decryption attempts are made. If the integrity check fails, the decryption process is immediately aborted.

## 2. Memory Management

Python's standard strings are immutable, meaning they cannot be modified in-place and may linger in memory until garbage collected, posing a security risk for sensitive data like master passwords.

To mitigate this, the application utilizes a custom `SecureString` implementation:
-   **Mutable Buffers:** It creates mutable byte buffers in C-memory space, bypassing Python's immutable string interning restrictions.
-   **Secure Wiping:** Upon exiting the context manager (`__exit__`), `ctypes.memset` is explicitly called to zeroize the buffer, ensuring the sensitive data is actively wiped from RAM rather than waiting for garbage collection.

## 3. Application Security Layer

### Brute-Force Protection
To defend against offline and online brute-force attacks on the vault unlock mechanism:
-   **Exponential Login Backoff:** The application enforces an exponentially increasing wait time (`lockout_until`) after sequential invalid unlock attempts.
-   **Maximum Lockout:** The backoff period is capped at a maximum of 5 minutes per failed attempt after reaching the threshold.

### Active Protection & Auto-Lock
To protect the vault when the user is away from their device:
-   **Idle Detection:** Global input listeners (`pynput`) monitor system-wide keyboard and mouse activity.
-   **Automatic Lockout:** If no input is detected for a period exceeding 300 seconds (5 minutes), the application triggers an automatic vault lockout, requiring the master password to re-access the data.

## 4. Vulnerability Reporting

If you discover a security vulnerability within this project, please report it immediately. Do not disclose the vulnerability publicly until it has been addressed.
