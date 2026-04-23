
## 2026-04-23 - [Clipboard Information Leakage]
**Vulnerability:** Passwords copied to the clipboard remained indefinitely and were also unnecessarily copied when the Omni Login feature was used.
**Learning:** The clipboard is a global resource accessible by other applications. Leaving sensitive data there increases the risk of interception. Auto-type features should bypass the clipboard entirely.
**Prevention:** Automatically clear the clipboard after a short duration (e.g., 30s) if its contents haven't changed, and avoid copying to the clipboard entirely when alternative methods (like simulated keystrokes) are used.
