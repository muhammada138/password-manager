import os
import sys
import getpass
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Import the NEW vault class from the local directory
try:
    from vault import IncrementalVault as NewVault
except ImportError:
    print("Error: Could not import NewVault from vault.py. Run this script from the new project directory.")
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

def main():
    print("--- OmniVault Legacy Importer ---")
    old_path = input("Enter path to old vault (default: C:\\projects\\password-manager\\my_vault.bin): ").strip()
    if not old_path:
        old_path = r"C:\projects\password-manager\my_vault.bin"
        
    if not os.path.exists(old_path):
        print(f"Error: Could not find old vault at {old_path}")
        return

    old_pwd = getpass.getpass("Enter password for OLD vault: ")
    old_vault = OldVault(old_pwd, old_path)
    
    if not old_vault.load():
        print("Error: Could not unlock old vault. Incorrect password or corrupted file.")
        return
        
    print(f"Successfully unlocked old vault!")
    
    new_path = "my_vault.bin"
    new_pwd = getpass.getpass("Enter master password for NEW vault (must match if you already created it): ")
    
    new_vault = NewVault(new_pwd, new_path)
    if not new_vault.load():
        print("Error: Could not load or create new vault.")
        return
        
    imported_count = 0
    apps = [k for k in old_vault.data.keys() if k != "__metadata__"]
    
    for app in apps:
        accounts = list(old_vault.data[app].keys())
        for acc in accounts:
            entry_dict = old_vault.get_entry(app, acc)
            if entry_dict:
                new_vault.set_entry(app, acc, entry_dict)
                imported_count += 1
                print(f"  Imported: {app} -> {acc}")
                
    new_vault.save()
    print(f"\nDone! Successfully imported {imported_count} credentials into the new vault.")

if __name__ == '__main__':
    main()
