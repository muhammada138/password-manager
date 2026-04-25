import json
import os
import base64
import ctypes
import hmac
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

class SecureString:
    """Context manager for securely handling sensitive strings, zeroing memory after use."""
    def __init__(self, string_data):
        if isinstance(string_data, str):
            string_data = string_data.encode('utf-8')
        self._length = len(string_data)
        self._buffer = ctypes.create_string_buffer(string_data)

    def get_bytes(self):
        if not self._buffer:
            raise RuntimeError("SecureString has been cleared.")
        return self._buffer.raw[:self._length]

    def get_str(self):
        return self.get_bytes().decode('utf-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def clear(self):
        if self._buffer:
            ctypes.memset(ctypes.addressof(self._buffer), 0, self._length)
            self._buffer = None

class IncrementalVault:
    def __init__(self, password: str, vault_path="my_vault.bin"):
        self._password = password
        self.vault_path = vault_path
        self.salt = None
        self.fernet_key = None
        self.hmac_key = None
        self.data = {}

    def _derive_keys(self, salt):
        with SecureString(self._password) as sec_pw:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=64,
                salt=salt,
                iterations=200000,
            )
            derived = kdf.derive(sec_pw.get_bytes())
            self.fernet_key = base64.urlsafe_b64encode(derived[:32])
            self.hmac_key = derived[32:]

    def _encrypt_data(self, data: bytes) -> bytes:
        f = Fernet(self.fernet_key)
        ciphertext = f.encrypt(data)
        h = hmac.new(self.hmac_key, ciphertext, hashlib.sha256)
        return ciphertext + h.digest()

    def _decrypt_data(self, data: bytes) -> bytes:
        if len(data) < 32:
            raise ValueError("Data too short")
        ciphertext = data[:-32]
        mac = data[-32:]
        h = hmac.new(self.hmac_key, ciphertext, hashlib.sha256)
        if not hmac.compare_digest(h.digest(), mac):
            raise InvalidKey("HMAC integrity check failed")
        f = Fernet(self.fernet_key)
        return f.decrypt(ciphertext)

    def load(self, callback=None):
        if not os.path.exists(self.vault_path):
            self.salt = os.urandom(16)
            self._derive_keys(self.salt)
            self.data = {}
            if callback: callback(True)
            return True

        try:
            with open(self.vault_path, "rb") as f:
                self.salt = f.read(16)
                encrypted_data = f.read()
            
            self._derive_keys(self.salt)
            decrypted_data = self._decrypt_data(encrypted_data)
            self.data = json.loads(decrypted_data.decode('utf-8'))
            
            if callback: callback(True)
            return True
        except Exception:
            if callback: callback(False)
            return False

    def save(self):
        json_data = json.dumps(self.data).encode('utf-8')
        encrypted_data = self._encrypt_data(json_data)
        with open(self.vault_path, "wb") as f:
            f.write(self.salt + encrypted_data)

    def get_entry(self, app_name, acc_name):
        encrypted_entry = self.data.get(app_name, {}).get(acc_name)
        if not encrypted_entry:
            return None
        
        if isinstance(encrypted_entry, dict):
            return encrypted_entry
            
        try:
            encrypted_bytes = base64.b64decode(encrypted_entry.encode('ascii'))
            decrypted_entry = self._decrypt_data(encrypted_bytes)
            return json.loads(decrypted_entry.decode('utf-8'))
        except Exception:
            return None

    def set_entry(self, app_name, acc_name, entry_dict):
        if app_name not in self.data:
            self.data[app_name] = {}
        
        encrypted_bytes = self._encrypt_data(json.dumps(entry_dict).encode('utf-8'))
        encrypted_entry = base64.b64encode(encrypted_bytes).decode('ascii')
        self.data[app_name][acc_name] = encrypted_entry

    def delete_entry(self, app_name, acc_name):
        if app_name in self.data and acc_name in self.data[app_name]:
            del self.data[app_name][acc_name]

            if "__metadata__" in self.data and "acc_order" in self.data["__metadata__"] and app_name in self.data["__metadata__"]["acc_order"]:
                if acc_name in self.data["__metadata__"]["acc_order"][app_name]:
                    self.data["__metadata__"]["acc_order"][app_name].remove(acc_name)

            if not self.data[app_name]:
                del self.data[app_name]
                if "__metadata__" in self.data:
                    if "app_order" in self.data["__metadata__"] and app_name in self.data["__metadata__"]["app_order"]:
                        self.data["__metadata__"]["app_order"].remove(app_name)
                    if "acc_order" in self.data["__metadata__"] and app_name in self.data["__metadata__"]["acc_order"]:
                        del self.data["__metadata__"]["acc_order"][app_name]

    def delete_app(self, app_name):
        if app_name in self.data:
            del self.data[app_name]
            if "__metadata__" in self.data:
                if "app_order" in self.data["__metadata__"] and app_name in self.data["__metadata__"]["app_order"]:
                    self.data["__metadata__"]["app_order"].remove(app_name)
                if "acc_order" in self.data["__metadata__"] and app_name in self.data["__metadata__"]["acc_order"]:
                    del self.data["__metadata__"]["acc_order"][app_name]

    def set_app_order(self, order_list):
        if "__metadata__" not in self.data:
            self.data["__metadata__"] = {}
        self.data["__metadata__"]["app_order"] = order_list

    def get_apps(self):
        apps = [k for k in self.data.keys() if k != "__metadata__"]
        order = self.data.get("__metadata__", {}).get("app_order", [])
        # Performance optimization (Bolt): Pre-compute dictionary for O(1) index lookups
        # Expected impact: Improves sorting from O(n^2 log n) to O(n log n) by avoiding list.index() in the key function
        order_idx = {app: i for i, app in enumerate(order)}
        default_idx = len(order)
        return sorted(apps, key=lambda x: order_idx.get(x, default_idx))

    def set_account_order(self, app_name, order_list):
        if "__metadata__" not in self.data:
            self.data["__metadata__"] = {}
        if "acc_order" not in self.data["__metadata__"]:
            self.data["__metadata__"]["acc_order"] = {}
        self.data["__metadata__"]["acc_order"][app_name] = order_list

    def get_accounts(self, app_name):
        accounts = [k for k in self.data.get(app_name, {}).keys()]
        order = self.data.get("__metadata__", {}).get("acc_order", {}).get(app_name, [])
        # Performance optimization (Bolt): Pre-compute dictionary for O(1) index lookups
        # Expected impact: Improves sorting from O(n^2 log n) to O(n log n) by avoiding list.index() in the key function
        order_idx = {acc: i for i, acc in enumerate(order)}
        default_idx = len(order)
        return sorted(accounts, key=lambda x: order_idx.get(x, default_idx))
