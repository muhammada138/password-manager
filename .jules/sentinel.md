## 2026-04-24 - Clipboard Security & Omni Login Bypass
**Vulnerability:** Passwords unconditionally copied to clipboard and never cleared, exposing them to clipboard-sniffing malware, especially when Omni Login automated typing bypasses the need for the clipboard.
**Learning:** System clipboards are universally readable by background applications. Passing sensitive credentials through the clipboard should be avoided when possible.
**Prevention:** Implement auto-clearing timeouts (e.g., 30s) for sensitive clipboard contents and completely bypass clipboard operations when alternative secure delivery methods (like direct keystroke injection) are enabled.
