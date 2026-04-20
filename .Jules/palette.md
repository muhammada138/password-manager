## 2024-05-24 - Accessibility for Frameless Window Controls and Tray Icons
**Learning:** Custom frameless windows in PyQt6 lose default OS accessibility properties. Icon-only buttons (like minimize/close) and tray icons without explicit labels become "invisible" or unhelpful to screen readers and lack hover context, reducing usability.
**Action:** Always assign `setToolTip()` and `setAccessibleName()` to custom window control buttons and `setToolTip()` to `QSystemTrayIcon` instances to restore critical context and screen reader compatibility.
