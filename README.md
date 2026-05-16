# OmniVault

A high-performance desktop security tool designed for local-first credential management. It provides a secure and efficient way to store your sensitive data using industry-standard encryption protocols, featuring an automated typing system and a refined dark-mode interface for a seamless user experience.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=flat&logo=qt&logoColor=white)
![Cryptography](https://img.shields.io/badge/Cryptography-Fernet+HMAC-blue?style=flat)
![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-auto--typing-orange?style=flat)

---

## What it does

OmniVault is a secure, offline-first password manager built with Python and PyQt6. Instead of trusting your passwords to the cloud, everything is encrypted locally using Fernet symmetric encryption and a PBKDF2 derived key with an HMAC-SHA256 integrity layer. It lives in your system tray and features a unique "Click & Type" login logic to protect against clipboard hijacking.

**Key features:**

- **Layered Cryptography** - Stores credentials in an encrypted binary vault (`my_vault.bin`) using Fernet (AES-128 in CBC mode) with a PBKDF2HMAC (SHA-256, 200,000 iterations) derived key.
- **HMAC-SHA256 Integrity Layer** - Employs an Encrypt-then-MAC architecture utilizing `hmac.compare_digest` to verify ciphertexts before decryption, preventing tampering.
- **Secure Memory Wiping** - Custom `SecureString` context manager leveraging `ctypes.memset` to zeroize the master password from memory immediately after key derivation.
- **Local-Only Storage** - Zero cloud connectivity. Your data never leaves your machine.
- **Frameless Premium UI** - A sleek, custom PyQt6 interface with a Midnight Blue/Slate color scheme, Electric Blue accents, drop-shadows, drag-and-drop sorting, and right-click context menus.
- **Active Security Features** - Includes exponential login backoff to mitigate brute force attempts and an auto-lockout mechanism triggered by 5 minutes of system-wide idle time.
- **Standalone Executable** - OmniVault can be compiled into a single `.exe` file that natively bundles its custom icon and runs completely standalone.
- **System Tray Integration** - Runs quietly in the background (via `QSystemTrayIcon`) and can be summoned instantly via a global hotkey (`Ctrl + P`).
- **"Click & Type" Omni Login** - To prevent clipboard sniffing, OmniVault uses PyAutoGUI to simulate human keystrokes directly into targeted input fields automatically.
- **Start with Windows** - Optional registry toggle to automatically launch the vault silently when you boot your PC.

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend / GUI | Python `PyQt6` |
| Security / Cryptography | `cryptography` (Fernet, PBKDF2HMAC, SHA-256), `hmac`, `ctypes` |
| Automation & System | `pyautogui`, `pynput`, `winreg` |

---

## Getting started

You need Python 3.10+ installed on your Windows system.

### Installation

```bash
git clone https://github.com/muhammada138/password-manager.git
cd password-manager
pip install -r requirements.txt
```

### Running the App

```bash
python secure_switcher.py
```

On first launch, you will be prompted to create/enter a vault password. This password derives the encryption key for the entire `my_vault.bin` file.

**Global Hotkey:** `Ctrl + P` to toggle the vault window visibility from anywhere.

---

## Building a Standalone Executable

You can compile OmniVault into a single `.exe` that runs without Python installed.

**Requirements:** PyInstaller must be installed (`pip install pyinstaller` or `pip install -r requirements.txt`).

**Build:**

```bash
rebuild.bat
```

This will produce `OmniVault.exe` in the project folder. Double-click it — no Python required on the target machine.

> **Note:** Windows Defender or antivirus software may flag PyInstaller-packaged executables as a false positive. This is a known PyInstaller limitation. You can safely add an exclusion, or run from source instead.

---

## Security Considerations

- **No Hardcoded Keys:** Your vault is entirely encrypted and decrypted in memory. The key is securely derived from your master password using PBKDF2HMAC with 200,000 iterations and a random salt stored alongside the encrypted blob.
- **Secure Memory Management:** `ctypes.memset` zeroizes sensitive data such as your master password in RAM immediately upon use to mitigate cold-boot or memory-dump attacks.
- **Clipboard Protection:** Standard password managers copy credentials to your clipboard, leaving them vulnerable to clipboard-sniffing malware. OmniVault's optional "Omni Login" logic bypasses the clipboard completely for password injection by typing it out for you.
- **Git Security:** `my_vault.bin`, `settings.json`, and other sensitive files are explicitly ignored via `.gitignore` to ensure your encrypted vault and keys are never accidentally pushed to version control.
