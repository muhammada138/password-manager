## 2024-05-15 - [Prevent Clipboard Sniffing]
**Vulnerability:** Passwords copied to the clipboard can be sniffed by malicious software running in the background. The OmniVault logic to copy passwords to the clipboard wasn't correctly bypassing this for the "Omni Login" mode and lacked an automatic clearing timeout.
**Learning:** Even when security features like "Omni Login" (auto-typing) are implemented, care must be taken to ensure they don't accidentally fall back to insecure methods (like clipboard copying). Additionally, any sensitive data placed in the clipboard must have a strict TTL (Time To Live).
**Prevention:**
1. Conditional clipboard usage: Ensure password copying logic explicitly checks the user's preference for auto-typing vs clipboard.
2. Automatic clipboard clearing: Implement a timer (e.g., `QTimer.singleShot(30000, QApplication.clipboard().clear)` in PyQt6) to automatically wipe the clipboard after a short duration when a password is copied.
