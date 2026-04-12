import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class IncrementalVault:
    def __init__(self, password, vault_path="my_vault.bin"):
        self.password = password
        self.vault_path = vault_path
        self.salt = None
        self.fernet = None
        self.data = {} # {app_name: {acc_name: encrypted_entry_blob}}

    def _derive_key(self, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password.encode()))

    def load(self, callback=None):
        """Load the vault index. Decryption happens in a way that can be offloaded."""
        if not os.path.exists(self.vault_path):
            self.salt = os.urandom(16)
            self.fernet = Fernet(self._derive_key(self.salt))
            self.data = {}
            if callback: callback(True)
            return True

        try:
            with open(self.vault_path, "rb") as f:
                self.salt = f.read(16)
                encrypted_data = f.read()
            
            self.fernet = Fernet(self._derive_key(self.salt))
            decrypted_data = self.fernet.decrypt(encrypted_data)
            self.data = json.loads(decrypted_data.decode())
            
            if callback: callback(True)
            return True
        except Exception:
            if callback: callback(False)
            return False

    def save(self):
        """Save the vault index."""
        json_data = json.dumps(self.data).encode()
        encrypted_data = self.fernet.encrypt(json_data)
        with open(self.vault_path, "wb") as f:
            f.write(self.salt + encrypted_data)

    def get_entry(self, app_name, acc_name):
        """Decrypt and return a single entry on demand."""
        encrypted_entry = self.data.get(app_name, {}).get(acc_name)
        if not encrypted_entry:
            return None
        
        # If it's already a dict, it's an old format or already decrypted
        if isinstance(encrypted_entry, dict):
            return encrypted_entry
            
        try:
            decrypted_entry = self.fernet.decrypt(encrypted_entry.encode())
            return json.loads(decrypted_entry.decode())
        except Exception:
            return None

    def set_entry(self, app_name, acc_name, entry_dict):
        """Encrypt and store a single entry."""
        if app_name not in self.data:
            self.data[app_name] = {}
        
        encrypted_entry = self.fernet.encrypt(json.dumps(entry_dict).encode()).decode()
        self.data[app_name][acc_name] = encrypted_entry

    def delete_entry(self, app_name, acc_name):
        if app_name in self.data and acc_name in self.data[app_name]:
            del self.data[app_name][acc_name]
            if not self.data[app_name]:
                del self.data[app_name]

    def delete_app(self, app_name):
        if app_name in self.data:
            del self.data[app_name]

    def get_apps(self):
        return sorted(self.data.keys())

    def get_accounts(self, app_name):
        return sorted(self.data.get(app_name, {}).keys())
