# OmniVault

A modern, frameless desktop password manager featuring military-grade encryption, hotkey-driven auto-typing, and a streamlined slate/blue UI. Designed as an ultra-secure, local-only alternative to cloud-based password managers.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-000000?style=flat)
![Cryptography](https://img.shields.io/badge/Cryptography-Fernet-blue?style=flat)
![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-auto--typing-orange?style=flat)

---

## What it does

OmniVault is a secure, offline-first password manager built with Python and Tkinter. Instead of trusting your passwords to the cloud, everything is encrypted locally using Fernet symmetric encryption and a PBKDF2 derived key. It lives in your system tray and features a unique "Click & Type" login logic to protect against clipboard hijacking.

**Key features:**

- **Military-Grade Encryption** - Stores credentials in an encrypted binary vault (`my_vault.bin`) using Fernet (AES-128 in CBC mode) with a PBKDF2HMAC (SHA-256) derived key.
- **Local-Only Storage** - Zero cloud connectivity. Your data never leaves your machine.
- **Frameless Modern UI** - A sleek, custom Tkinter interface with a slate and blue color scheme, custom toggle switches, memory-efficient color-fade hover animations, and a draggable reordering system.
- **Standalone Executable** - OmniVault can be compiled into a single `.exe` file that natively bundles its custom icon and runs completely standalone.
- **System Tray Integration** - Runs quietly in the background (via `pystray`) and can be summoned instantly via a global hotkey (`Ctrl + P`).
- **"Click & Type" Omni Login** - To prevent clipboard sniffing, OmniVault uses PyAutoGUI to simulate human keystrokes directly into targeted input fields. You click the login button, wait for the mouse release, then click the target username/email field, and the app types it out for you.
- **Start with Windows** - Optional registry toggle to automatically launch the vault when you boot your PC.
- **Incremental Decryption** - Decrypts individual account entries only on demand.

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend / GUI | Python `tkinter`, `PIL` |
| Security / Cryptography | `cryptography` (Fernet, PBKDF2HMAC, SHA-256) |
| Automation & System | `pyautogui`, `pystray`, `winreg`, `ctypes` |

---

## Getting started

You need Python 3.10+ installed on your Windows system.

### Installation

```bash
git clone https://github.com/muhammada138/password-manager.git
cd password-manager
pip install cryptography pyautogui pystray pillow
```

### Running the App

```bash
python secure_switcher.py
```

On first launch, you will be prompted to create/enter a vault password. This password derives the encryption key for the entire `my_vault.bin` file.

**Global Hotkey:** `Ctrl + P` to toggle the vault window visibility from anywhere.

---

## Security Considerations

- **No Hardcoded Keys:** Your vault is entirely encrypted and decrypted in memory. The key is securely derived from your master password using PBKDF2HMAC with 100,000 iterations and a random salt stored alongside the encrypted blob.
- **Clipboard Protection:** Standard password managers copy credentials to your clipboard, leaving them vulnerable to clipboard-sniffing malware. OmniVault's optional "Click & Type" logic bypasses the clipboard completely for password injection.
- **Git Security:** `my_vault.bin`, `key.key`, and `settings.json` are explicitly ignored via `.gitignore` to ensure your encrypted vault and keys are never accidentally pushed to version control.
