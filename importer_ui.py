import sys
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QMessageBox)

# Import the new vault logic
try:
    from vault import IncrementalVault as NewVault
except ImportError:
    print("Error: Could not import NewVault from vault.py.")
    sys.exit(1)

class OldVault:
    def __init__(self, password, vault_path):
        self.password = password
        self.vault_path = vault_path
        self.salt = None
        self.fernet = None
        self.data = {}

    def _derive_key(self, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password.encode()))

    def load(self):
        if not os.path.exists(self.vault_path):
            return False
        try:
            with open(self.vault_path, "rb") as f:
                self.salt = f.read(16)
                encrypted_data = f.read()

            self.fernet = Fernet(self._derive_key(self.salt))
            decrypted_data = self.fernet.decrypt(encrypted_data)
            self.data = json.loads(decrypted_data.decode())
            return True
        except Exception:
            return False

    def get_entry(self, app_name, acc_name):
        encrypted_entry = self.data.get(app_name, {}).get(acc_name)
        if not encrypted_entry:
            return None
        if isinstance(encrypted_entry, dict):
            return encrypted_entry
        try:
            decrypted_entry = self.fernet.decrypt(encrypted_entry.encode())
            return json.loads(decrypted_entry.decode())
        except Exception:
            return None

class ImporterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmniVault Importer")
        self.resize(450, 350)
        self.setStyleSheet("background-color: #0F172A; color: #F8FAFC; font-family: 'Segoe UI';")
        
        layout = QVBoxLayout(self)
        
        self.title = QLabel("Import Legacy Vault")
        self.title.setStyleSheet("font-size: 20px; color: #38BDF8; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.title)

        self.path_input = QLineEdit(r"C:\projects\password-manager\my_vault.bin")
        self.path_input.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; padding: 8px; border-radius: 4px;")
        layout.addWidget(QLabel("Old Vault Path:"))
        layout.addWidget(self.path_input)

        self.old_pwd = QLineEdit()
        self.old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_pwd.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; padding: 8px; border-radius: 4px;")
        layout.addWidget(QLabel("Old Master Password:"))
        layout.addWidget(self.old_pwd)

        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pwd.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; padding: 8px; border-radius: 4px;")
        layout.addWidget(QLabel("New Master Password (for the new app):"))
        layout.addWidget(self.new_pwd)

        self.import_btn = QPushButton("Import Vault")
        self.import_btn.setStyleSheet("background-color: #38BDF8; color: #0F172A; font-weight: bold; padding: 10px; border-radius: 4px; margin-top: 10px;")
        self.import_btn.clicked.connect(self.do_import)
        layout.addWidget(self.import_btn)

    def do_import(self):
        old_path = self.path_input.text()
        old_pwd = self.old_pwd.text()
        new_pwd = self.new_pwd.text()

        if not os.path.exists(old_path):
            QMessageBox.critical(self, "Error", "Old vault file not found at the specified path!")
            return

        if not old_pwd or not new_pwd:
            QMessageBox.critical(self, "Error", "Please enter both passwords!")
            return

        # Load old vault
        old_vault = OldVault(old_pwd, old_path)
        if not old_vault.load():
            QMessageBox.critical(self, "Error", "Could not unlock old vault. Incorrect password or corrupted file.")
            return

        # Load or create new vault in current directory
        new_path = "my_vault.bin"
        new_vault = NewVault(new_pwd, new_path)
        if not new_vault.load():
            QMessageBox.critical(self, "Error", "Could not load or create new vault.")
            return

        # Migrate data
        imported_count = 0
        apps = [k for k in old_vault.data.keys() if k != "__metadata__"]
        
        for app in apps:
            accounts = list(old_vault.data[app].keys())
            for acc in accounts:
                entry_dict = old_vault.get_entry(app, acc)
                if entry_dict:
                    new_vault.set_entry(app, acc, entry_dict)
                    imported_count += 1
                    
        new_vault.save()
        QMessageBox.information(self, "Success", f"Successfully imported {imported_count} credentials into the new highly secure vault!\n\nYou can now close this window and run the main OmniVault app.")
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImporterApp()
    window.show()
    sys.exit(app.exec())