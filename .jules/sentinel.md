## 2024-04-30 - Increase PBKDF2 Iterations to 600k
**Vulnerability:** Weak PBKDF2 iteration count (200,000) for key derivation from master password.
**Learning:** Older iteration counts become insufficient as hardware accelerates. Increasing the iterations strengthens resistance against offline brute-force attacks. Backward compatibility must be maintained for existing users during security upgrades to prevent data loss or lockouts.
**Prevention:** Regularly review and update cryptographic parameters (like PBKDF2 iterations) to align with current OWASP recommendations and hardware capabilities, ensuring legacy data decryption paths remain intact.
