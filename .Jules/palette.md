## 2024-05-24 - Accessibility attributes for frameless window components
**Learning:** Custom frameless UI components and system tray icons lack native accessible names and tooltips.
**Action:** Always assign `setToolTip()` and `setAccessibleName()` to custom icon-only buttons (like minimize/close in a custom TitleBar) and QSystemTrayIcon instances to maintain screen reader support.
