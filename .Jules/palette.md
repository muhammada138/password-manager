## 2024-05-24 - Accessibility for PyQt6 Icon-Only Buttons and System Tray
**Learning:** PyQt6 custom frameless windows with icon-only buttons (like minimize/close) and QSystemTrayIcon do not inherently provide screen reader contexts or tooltips, severely impacting accessibility.
**Action:** Always assign `setToolTip()` and `setAccessibleName()` to icon-only buttons in frameless windows, and `setToolTip()` to QSystemTrayIcon instances to maintain accessibility and screen reader support.
