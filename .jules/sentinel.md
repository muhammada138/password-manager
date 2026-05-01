## 2024-05-01 - Enhance PBKDF2 Iteration Count
**Vulnerability:** Weak key derivation iteration count (200,000) for PBKDF2HMAC, making offline brute-force attacks more feasible.
**Learning:** Security parameters like iteration counts must evolve. When upgrading such parameters, backward compatibility mechanisms (like try-except fallbacks) are essential to prevent data loss or lockout for existing users.
**Prevention:** Regularly review and update cryptographic parameters to align with current OWASP/NIST recommendations.
