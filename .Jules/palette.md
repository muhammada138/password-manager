## 2026-04-23 - Explicit Accessibility for Frameless Controls
**Learning:** PyQt6 frameless custom windows and icon-only controls (like close/minimize buttons and QSystemTrayIcon) often lack semantic meaning to screen readers and tooltips for standard users by default. Relying purely on visual layout is an accessibility anti-pattern.
**Action:** Always explicitly assign `setToolTip()` and `setAccessibleName()` to non-text or icon-only interactive elements to ensure they are discoverable and navigable via assistive technologies.
