import tkinter as tk
from tkinter import simpledialog, messagebox
import pyautogui
import time
import json
import base64
import sys
import winreg
import os
import ctypes
from ctypes import wintypes
import threading
from PIL import Image, ImageDraw
import pystray
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, variable, command=None, bg="#0f1923", active_color="#d13639", *args, **kwargs):
        super().__init__(parent, width=40, height=20, bg=bg, highlightthickness=0, cursor="hand2", *args, **kwargs)
        self.variable = variable
        self.command = command
        self.active_color = active_color
        self.bg_color = "#5c5c5c"
        self.bind("<Button-1>", self.toggle)
        self.draw()

    def draw(self):
        self.delete("all")
        state = self.variable.get()
        fill_color = self.active_color if state else self.bg_color
        # Draw track
        self.create_oval(0, 0, 20, 20, fill=fill_color, outline="")
        self.create_oval(20, 0, 40, 20, fill=fill_color, outline="")
        self.create_rectangle(10, 0, 30, 20, fill=fill_color, outline="")
        # Draw knob
        knob_x = 30 if state else 10
        self.create_oval(knob_x-8, 2, knob_x+8, 18, fill="white", outline="")

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
        self.draw()
        if self.command:
            self.command()

class ModernMenu(tk.Toplevel):
    def __init__(self, parent, x, y, options):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg="#5c5c5c", padx=1, pady=1) # Border effect
        
        self.geometry(f"+{x}+{y}")
        self.attributes('-topmost', True)
        
        container = tk.Frame(self, bg="#1f2b36")
        container.pack(fill='both', expand=True)

        for label, command in options:
            btn = tk.Button(container, text=label, font=("Segoe UI", 10), 
                            bg="#1f2b36", fg="#ece8e1", activebackground="#d13639", activeforeground="white",
                            relief="flat", bd=0, anchor="w", padx=15, cursor="hand2",
                            command=lambda c=command: self.execute(c))
            btn.pack(fill='x', ipady=6)
            
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#2c3b4b"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#1f2b36"))
            
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_force()
        
    def execute(self, command):
        command()
        self.destroy()

class SecureSwitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Riot Manager")
        self.root.geometry("360x600")
        self.root.configure(bg="#0f1923")
        self.root.overrideredirect(True) # Frameless Modern Window
        self.root.attributes('-topmost', True)
        
        if os.path.exists("riot_icon.ico"):
            self.root.iconbitmap("riot_icon.ico")
        
        self.vault_data = {}
        self.current_app = None
        self.salt = None
        self.fernet = None
        self.x = 0
        self.y = 0

        # Custom Title Bar (Drag Area)
        self.title_bar = tk.Frame(root, bg="#1f2b36", height=35)
        self.title_bar.pack(fill='x', side='top')
        self.setup_title_bar()

        # Main Content Area
        self.content_frame = tk.Frame(root, bg="#0f1923")
        self.content_frame.pack(fill='both', expand=True, padx=25, pady=20)

        # Load Vault
        if not self.load_vault():
            sys.exit() # Close if user cancels or fails login

        # Check startup status
        self.startup_var = tk.BooleanVar(value=self.check_startup_status())
        self.tray_var = tk.BooleanVar(value=self.load_settings().get("tray", False))

        self.setup_hotkey()
        self.show_apps_view()

    def setup_title_bar(self):
        # Title
        tk.Label(self.title_bar, text="  RIOT MANAGER", bg="#1f2b36", fg="#d13639", 
                 font=("Segoe UI", 10, "bold")).pack(side='left', pady=8)
        
        # Close Button
        close_btn = tk.Button(self.title_bar, text="✕", command=self.root.destroy, 
                              bg="#1f2b36", fg="white", bd=0, font=("Arial", 12),
                              activebackground="#d13639", activeforeground="white", cursor="hand2")
        close_btn.pack(side='right', padx=10, pady=5)
        
        # Minimize Button
        min_btn = tk.Button(self.title_bar, text="_", command=self.minimize_window,
                            bg="#1f2b36", fg="white", bd=0, font=("Arial", 12, "bold"),
                            activebackground="#1f2b36", activeforeground="#d13639", cursor="hand2")
        min_btn.pack(side='right', padx=0, pady=5)

        # Drag Logic
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def minimize_window(self):
        if self.tray_var.get():
            self.root.withdraw()
            self.run_tray_icon()
        else:
            # Temporarily disable frameless mode so it minimizes to taskbar correctly
            self.root.overrideredirect(False)
            self.root.iconify()
            self.root.bind('<Map>', self.restore_window)

    def restore_window(self, event):
        # Restore frameless mode when window is opened again
        if self.root.state() == 'normal':
            self.root.overrideredirect(True)
            self.root.unbind('<Map>')

    def run_tray_icon(self):
        image = self.create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem('Show', self.on_tray_show, default=True),
            pystray.MenuItem('Quit', self.on_tray_quit)
        )
        self.icon = pystray.Icon("RiotManager", image, "Riot Manager", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def setup_hotkey(self):
        threading.Thread(target=self.hotkey_loop, daemon=True).start()

    def hotkey_loop(self):
        # Register Ctrl + P (MOD_CONTROL=0x0002, 'P'=0x50)
        if not ctypes.windll.user32.RegisterHotKey(None, 1, 0x0002, 0x50):
            print("Failed to register hotkey")
            return

        msg = wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == 0x0312: # WM_HOTKEY
                self.root.after(0, self.toggle_app_visibility)
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

    def toggle_app_visibility(self):
        if self.root.state() == 'normal':
            self.minimize_window()
        else:
            self.restore_app()

    def restore_app(self):
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
        self.root.deiconify()
        if not self.root.overrideredirect():
            self.root.overrideredirect(True)
            self.root.unbind('<Map>')
        self.root.lift()
        self.root.focus_force()

    def create_tray_image(self):
        if os.path.exists("riot_icon.ico"):
            return Image.open("riot_icon.ico")
            
        # Create a 64x64 icon: Dark background with Red square
        image = Image.new('RGB', (64, 64), color="#0f1923")
        d = ImageDraw.Draw(image)
        d.rectangle([16, 16, 48, 48], fill="#d13639")
        return image

    def on_tray_show(self, icon, item):
        self.restore_app()

    def on_tray_quit(self, icon, item):
        icon.stop()
        self.root.after(0, self.root.destroy)

    def get_key(self, password, salt):
        """Re-derive the key using the same logic as setup."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def load_vault(self):
        if not os.path.exists("my_vault.bin"):
            return self.create_new_vault()

        try:
            with open("my_vault.bin", "rb") as file:
                file_content = file.read()
                
            # Extract Salt (first 16 bytes) and Data
            self.salt = file_content[:16]
            encrypted_data = file_content[16:]
            
            # Prompt for Master Password
            # Since this runs on startup, this dialog will wait for you
            # pwd = simpledialog.askstring("Unlock Vault", "Enter Master Password:", show='*', parent=self.root)
            pwd = "dev"

            key = self.get_key(pwd, self.salt)
            self.fernet = Fernet(key)
            
            # Decrypt
            decrypted_data = self.fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
            
            # Migration: Check if old flat format
            if data and isinstance(next(iter(data.values())), (list, tuple)):
                self.vault_data = {
                    "Riot Games": {
                        k: {"username": v[0], "password": v[1], "riot_logic": True}
                        for k, v in data.items()
                    }
                }
                self.save_vault()
            else:
                self.vault_data = data
            return True
            
        except InvalidToken:
            messagebox.showerror("Error", "Wrong Password!")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Crash: {str(e)}")
            return False

    def create_new_vault(self):
        if not messagebox.askyesno("Welcome", "No vault found. Create a new secure vault?"):
            return False
        
        # pwd = simpledialog.askstring("Setup", "Create a Master Password:", show='*', parent=self.root)
        pwd = "dev"
        
        self.salt = os.urandom(16)
        key = self.get_key(pwd, self.salt)
        self.fernet = Fernet(key)
        self.vault_data = {}
        self.save_vault()
        return True

    def save_vault(self):
        try:
            data = json.dumps(self.vault_data).encode()
            encrypted_data = self.fernet.encrypt(data)
            with open("my_vault.bin", "wb") as f:
                f.write(self.salt + encrypted_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save vault: {e}")

    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    return json.load(f)
            except:
                pass
        return {"tray": False}

    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump({"tray": self.tray_var.get()}, f)

    def create_scrollable_frame(self, parent):
        container = tk.Frame(parent, bg="#0f1923")
        container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(container, bg="#0f1923", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg="#0f1923")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        def configure_canvas(event):
            canvas.itemconfig(window_id, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        
        return scroll_frame

    def show_apps_view(self):
        self.current_app = None
        # Clear current view
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header
        tk.Label(self.content_frame, text="APPLICATIONS", font=("Segoe UI", 14, "bold"), 
                 bg="#0f1923", fg="#ece8e1").pack(anchor='w', pady=(0, 15))

        # Bottom Controls (Fixed at bottom)
        bottom_frame = tk.Frame(self.content_frame, bg="#0f1923")
        bottom_frame.pack(side='bottom', fill='x', pady=10)

        tk.Button(bottom_frame, text="+ NEW APPLICATION", 
                  font=("Segoe UI", 10, "bold"), bg="#1f2b36", fg="#ece8e1",
                  activebackground="#d13639", activeforeground="white",
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda: self.show_add_view(is_new_app=True)).pack(fill='x', pady=(0, 15), ipady=3)

        # Modern Toggles
        row1 = tk.Frame(bottom_frame, bg="#0f1923")
        row1.pack(fill='x', pady=5)
        ToggleSwitch(row1, self.startup_var, command=self.toggle_startup).pack(side='left')
        tk.Label(row1, text="Start with Windows", bg="#0f1923", fg="#ece8e1", font=("Segoe UI", 10)).pack(side='left', padx=10)

        row2 = tk.Frame(bottom_frame, bg="#0f1923")
        row2.pack(fill='x', pady=5)
        ToggleSwitch(row2, self.tray_var, command=self.save_settings).pack(side='left')
        tk.Label(row2, text="Minimize to Tray", bg="#0f1923", fg="#ece8e1", font=("Segoe UI", 10)).pack(side='left', padx=10)

        # Scrollable App List
        scroll_frame = self.create_scrollable_frame(self.content_frame)
        
        for app_name in self.vault_data:
            btn = tk.Button(scroll_frame, text=app_name.upper(), 
                          font=("Segoe UI", 11, "bold"),
                          bg="#ece8e1", fg="#0f1923",
                          activebackground="#d13639", activeforeground="white",
                          relief="flat", bd=0,
                          cursor="hand2",
                          command=lambda n=app_name: self.show_accounts_view(n))
            btn.pack(fill='x', pady=5, ipady=5)
            
            # Right click to delete
            btn.bind("<Button-3>", lambda event, n=app_name: self.show_app_context_menu(event, n))

    def show_accounts_view(self, app_name):
        self.current_app = app_name
        # Clear current view
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header with Back Button
        header = tk.Frame(self.content_frame, bg="#0f1923")
        header.pack(fill='x', pady=(0, 15), side='top')
        
        tk.Button(header, text="<", font=("Segoe UI", 12, "bold"), 
                  bg="#0f1923", fg="#d13639", bd=0, activebackground="#0f1923", activeforeground="white",
                  cursor="hand2", command=self.show_apps_view).pack(side='left')
                  
        tk.Label(header, text=app_name.upper(), font=("Segoe UI", 14, "bold"), 
                 bg="#0f1923", fg="#ece8e1").pack(side='left', padx=10)

        # Add Account Button (Fixed at bottom)
        tk.Button(self.content_frame, text="+ ADD ACCOUNT", 
                  font=("Segoe UI", 10, "bold"), bg="#1f2b36", fg="#ece8e1",
                  activebackground="#d13639", activeforeground="white",
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda: self.show_add_view(prefill_app=app_name)).pack(side='bottom', fill='x', pady=20, ipady=3)

        # Scrollable Account List
        scroll_frame = self.create_scrollable_frame(self.content_frame)

        accounts = self.vault_data.get(app_name, {})
        for acc_name in accounts:
            btn = tk.Button(scroll_frame, text=acc_name.upper(), 
                          font=("Segoe UI", 11, "bold"),
                          bg="#ece8e1", fg="#0f1923",
                          activebackground="#d13639", activeforeground="white",
                          relief="flat", bd=0,
                          cursor="hand2",
                          command=lambda n=acc_name: self.execute_login(app_name, n))
            btn.pack(fill='x', pady=5, ipady=5)
            
            btn.bind("<Button-3>", lambda event, n=acc_name: self.show_account_context_menu(event, app_name, n))

    def show_add_view(self, edit_app=None, edit_name=None, prefill_app=None, is_new_app=False):
        # Clear current view
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        title_text = "EDIT ACCOUNT" if edit_name else ("NEW APPLICATION" if is_new_app else "NEW ACCOUNT")
        tk.Label(self.content_frame, text=title_text, font=("Segoe UI", 14, "bold"), 
                 bg="#0f1923", fg="#ece8e1").pack(anchor='w', pady=(0, 20))

        # Styles
        lbl_style = {"bg": "#0f1923", "fg": "#ece8e1", "font": ("Segoe UI", 10)}
        entry_style = {"bg": "#1f2b36", "fg": "white", "insertbackground": "white", "relief": "flat"}

        tk.Label(self.content_frame, text="Application", **lbl_style).pack(anchor='w', pady=(5, 2))
        app_entry = tk.Entry(self.content_frame, **entry_style)
        app_entry.pack(fill='x', ipady=5, pady=(0, 10))
        if prefill_app: app_entry.insert(0, prefill_app)
        if edit_app: app_entry.insert(0, edit_app)

        tk.Label(self.content_frame, text="Account Name", **lbl_style).pack(anchor='w', pady=(5, 2))
        name_entry = tk.Entry(self.content_frame, **entry_style)
        name_entry.pack(fill='x', ipady=5, pady=(0, 10))

        tk.Label(self.content_frame, text="Username", **lbl_style).pack(anchor='w', pady=(5, 2))
        user_entry = tk.Entry(self.content_frame, **entry_style)
        user_entry.pack(fill='x', ipady=5, pady=(0, 10))

        # Password Row with Show Toggle
        pass_frame = tk.Frame(self.content_frame, bg="#0f1923")
        pass_frame.pack(fill='x', pady=(5, 2))
        tk.Label(pass_frame, text="Password", **lbl_style).pack(side='left')
        
        def toggle_pass_view():
            if pass_entry.cget('show') == '*':
                pass_entry.config(show='')
                show_btn.config(text="Hide")
            else:
                pass_entry.config(show='*')
                show_btn.config(text="Show")

        show_btn = tk.Button(pass_frame, text="Show", command=toggle_pass_view,
                             bg="#0f1923", fg="#d13639", bd=0, font=("Segoe UI", 8), cursor="hand2", activebackground="#0f1923")
        show_btn.pack(side='right')

        pass_entry = tk.Entry(self.content_frame, show="*", **entry_style)
        pass_entry.pack(fill='x', ipady=5, pady=(0, 10))

        # Riot Logic Toggle
        riot_var = tk.BooleanVar(value=False)
        riot_frame = tk.Frame(self.content_frame, bg="#0f1923")
        riot_frame.pack(fill='x', pady=10)
        ToggleSwitch(riot_frame, riot_var).pack(side='left')
        tk.Label(riot_frame, text="Use Riot Login (Click & Type)", **lbl_style).pack(side='left', padx=10)

        if edit_name and edit_app:
            data = self.vault_data[edit_app][edit_name]
            name_entry.insert(0, edit_name)
            user_entry.insert(0, data['username'])
            pass_entry.insert(0, data['password'])
            riot_var.set(data.get('riot_logic', False))

        def save():
            app = app_entry.get().strip()
            name = name_entry.get().strip()
            user = user_entry.get().strip()
            pwd = pass_entry.get().strip()
            
            if not app or not name: 
                messagebox.showwarning("Error", "App and Account Name required.")
                return

            if app not in self.vault_data:
                self.vault_data[app] = {}
            
            # If editing, remove old entry if name changed
            if edit_name and edit_app and (edit_name != name or edit_app != app):
                del self.vault_data[edit_app][edit_name]
                if not self.vault_data[edit_app]: del self.vault_data[edit_app]

            self.vault_data[app][name] = {
                "username": user,
                "password": pwd,
                "riot_logic": riot_var.get()
            }
            self.save_vault()
            self.show_accounts_view(app)

        def cancel():
            if self.current_app:
                self.show_accounts_view(self.current_app)
            else:
                self.show_apps_view()

        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg="#0f1923")
        btn_frame.pack(fill='x', pady=10)

        tk.Button(btn_frame, text="SAVE", command=save, bg="#d13639", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", width=10).pack(side='left')
        
        tk.Button(btn_frame, text="CANCEL", command=cancel, bg="#1f2b36", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", width=10).pack(side='right')

    def show_app_context_menu(self, event, app_name):
        options = [
            (f"Delete {app_name}", lambda: self.delete_app(app_name))
        ]
        ModernMenu(self.root, event.x_root, event.y_root, options)

    def show_account_context_menu(self, event, app_name, acc_name):
        options = [
            (f"Edit {acc_name}", lambda: self.show_add_view(edit_app=app_name, edit_name=acc_name)),
            (f"Delete {acc_name}", lambda: self.delete_account(app_name, acc_name))
        ]
        ModernMenu(self.root, event.x_root, event.y_root, options)

    def delete_app(self, app_name):
        if messagebox.askyesno("Confirm", f"Delete entire application '{app_name}' and all passwords?"):
            del self.vault_data[app_name]
            self.save_vault()
            self.show_apps_view()

    def delete_account(self, app_name, acc_name):
        if messagebox.askyesno("Confirm", f"Delete account '{acc_name}'?"):
            del self.vault_data[app_name][acc_name]
            self.save_vault()
            self.show_accounts_view(app_name)

    def execute_login(self, app_name, account_name):
        data = self.vault_data[app_name][account_name]
        username = data['username']
        password = data['password']
        
        # Check if using Riot Logic
        if not data.get('riot_logic', False):
            # Standard Behavior: Copy "username : password" to Clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(f"{username} : {password}")
            self.root.update()
            
            # Auto send to tray
            self.root.withdraw()
            self.run_tray_icon()
            return
        
        # Riot Logic (Click & Type)
        self.root.withdraw()
        
        # Wait for mouse release (from clicking the button)
        while ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000:
            time.sleep(0.05)

        # Wait for next click (on the target input)
        while not (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000):
            time.sleep(0.05)
        
        time.sleep(0.2) 
        
        # Type Username (fast to avoid clipboard race conditions)
        pyautogui.write(username, interval=0)

        pyautogui.press('tab')
        time.sleep(0.1) # Wait for focus switch
        
        # Paste Password
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        time.sleep(0.1) # Wait for clipboard to update
        pyautogui.hotkey('ctrl', 'v')

        time.sleep(0.2)
        pyautogui.press('enter')
        
        self.root.deiconify()

    def check_startup_status(self):
        """Check if registry key exists."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "RiotSecureSwitcher")
            winreg.CloseKey(key)
            return True
        except:
            return False

    def toggle_startup(self):
        """Add or remove from Windows Startup."""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "RiotSecureSwitcher"
        # Use pythonw.exe to run without console
        exe_path = sys.executable.replace("python.exe", "pythonw.exe")
        script_path = os.path.abspath(__file__)
        command = f'"{exe_path}" "{script_path}"'

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if self.startup_var.get():
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Error", f"Startup setting failed: {e}")
            self.startup_var.set(not self.startup_var.get()) # Revert check

if __name__ == "__main__":
    # Fix for shortcut: Set working directory to the script's folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    root = tk.Tk()
    # Hide the main window initially until we know we have data
    root.withdraw() 
    
    app = SecureSwitcher(root)
    
    # If app loaded successfully, show window
    root.deiconify()
    root.mainloop()