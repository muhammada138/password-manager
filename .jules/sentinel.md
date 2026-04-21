## 2024-04-21 - [Clipboard Sniffing Vulnerability]
**Vulnerability:** The password was unconditionally copied to the system clipboard upon clicking an entry, even when the auto-type "Omni Login" feature (`riot_logic`) was enabled. Furthermore, passwords copied to the clipboard were left there indefinitely.
**Learning:** This exposed the password to other applications and potential clipboard sniffing malware, negating the security benefit of the auto-type feature.
**Prevention:** Always bypass the clipboard when `riot_logic` is active, and enforce a strict automatic timeout (e.g., 30 seconds) to clear sensitive data from the clipboard when standard copying is necessary.
