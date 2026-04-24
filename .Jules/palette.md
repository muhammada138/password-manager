## 2024-04-24 - Explicit Accessibility for Frameless Windows and Tray Icons
**Learning:** PyQt6 frameless custom windows and system tray icons do not automatically derive accessible names or tooltips from the application state. If relying on icon-only buttons or custom title bars, screen readers fail to announce the window or controls.
**Action:** Always explicitly assign `setToolTip()` and `setAccessibleName()` on `QSystemTrayIcon`, frameless `QMainWindow` instances, and icon-only custom controls to maintain accessibility and UX.
