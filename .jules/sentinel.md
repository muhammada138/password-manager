## 2024-04-28 - Clipboard Data Leakage & Auto-type Sniffing
**Vulnerability:** Passwords were unconditionally copied to the system clipboard and left there indefinitely, exposing them to clipboard-sniffing malware and accidental pasting.
**Learning:** For auto-type features ('riot_logic'), copying data to the clipboard before simulating keystrokes is an unnecessary risk that completely nullifies the security benefit of auto-type.
**Prevention:** Always implement automatic, time-bound clipboard clearing (e.g., `QTimer.singleShot(30000, clear_clipboard)`) for normal copies, and completely bypass clipboard operations when using direct input simulation features.
