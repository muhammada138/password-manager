## 2024-04-28 - QSystemTrayIcon Accessibility Crash
**Learning:** Adding `setAccessibleName()` to a PyQt `QSystemTrayIcon` causes a fatal crash because it inherits from `QObject`, not `QWidget`, and does not support this method.
**Action:** When improving accessibility for `QSystemTrayIcon`, strictly use `setToolTip()` and NEVER use `setAccessibleName()`. Standard custom window UI buttons (`QWidget` descendants) should still use both `setToolTip()` and `setAccessibleName()`.
