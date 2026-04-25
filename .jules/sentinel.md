## 2026-04-25 - [Fix clipboard password leakage]
**Vulnerability:** Passwords copied to the clipboard were never cleared, and the clipboard copy occurred even when "riot_logic" (a form of clipboard bypass for logins) was enabled.
**Learning:** For secure credential managers, all sensitive data placed on the clipboard must have a timeout (e.g. 30 seconds) to clear it, and we should bypass the clipboard completely when not necessary.
**Prevention:** Always schedule an automatic clipboard clear when placing sensitive data into it.
