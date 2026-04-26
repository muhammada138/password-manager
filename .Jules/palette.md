## 2024-04-26 - [Frameless Window Control Accessibility]
**Learning:** Custom frameless window controls (like minimize and close buttons built with icon text) lack native OS-level tooltips and accessible names. Icon-only buttons and System Tray Icons can also be confusing or inaccessible without explicit labels.
**Action:** Always add `setToolTip()` and `setAccessibleName()` to custom frameless UI controls and `setToolTip()` to QSystemTrayIcon to maintain accessibility and user context.
