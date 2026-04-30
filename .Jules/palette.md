## 2026-04-30 - Dynamic Lockout UI
**Learning:** When disabling custom-styled buttons dynamically (e.g., using `setEnabled(False)`), they may retain their active appearance if a distinct `:disabled` CSS state isn't defined, confusing users. Furthermore, inactive elements without context cause friction.
**Action:** Always define `:disabled` styles in Qt stylesheets to visually mute inactive elements, and pair the disabled state with a descriptive `setToolTip()` explaining why it's locked out and when it will be available again.
