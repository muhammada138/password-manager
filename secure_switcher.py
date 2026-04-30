import sys
import time
import math
import os
import json
import threading
try:
    import winreg
except ImportError:
    winreg = None
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QStackedWidget, QFrame, QMessageBox, QDialog, QFormLayout, QCheckBox,
                             QMenu, QInputDialog, QAbstractItemView, QSystemTrayIcon, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QAction, QColor
from pynput import keyboard, mouse
import pyautogui
import ctypes

from vault import IncrementalVault

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tray": True, "startup": False}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def set_startup(enable):
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "OmniVault"
    
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
    else:
        exe_path = os.path.abspath(sys.argv[0])
        
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_WRITE)
        if enable:
            # Add --startup flag so it knows to start in tray
            winreg.SetValueEx(registry_key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --startup')
        else:
            winreg.DeleteValue(registry_key, app_name)
        winreg.CloseKey(registry_key)
    except Exception:
        pass

STYLE_SHEET = """
QMainWindow {
    background-color: #0B1120;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #F8FAFC;
}
#TitleBar {
    background-color: #111827;
    border-bottom: 1px solid #1E293B;
}
#TitleBar QLabel {
    color: #38BDF8;
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 1px;
}
#TitleBar QPushButton {
    background-color: transparent;
    border: none;
    font-size: 16px;
    color: #94A3B8;
    padding: 5px;
    border-radius: 4px;
}
#TitleBar QPushButton:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}
#TitleBar #CloseBtn:hover {
    background-color: #EF4444;
    color: #FFFFFF;
}
#Sidebar {
    background-color: #111827;
    border-right: 1px solid #1E293B;
}
#Sidebar QPushButton {
    background-color: transparent;
    text-align: left;
    padding: 12px 18px;
    border: none;
    border-radius: 8px;
    margin: 4px 12px;
    font-size: 14px;
    font-weight: 500;
    color: #CBD5E1;
}
#Sidebar QPushButton:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}
#ContentArea {
    background-color: #0B1120;
}
QLineEdit {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px 15px;
    color: #F8FAFC;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid #38BDF8;
    background-color: #0F172A;
}
QLineEdit:disabled {
    background-color: #0F172A;
    color: #475569;
    border: 1px solid #1E293B;
}
QPushButton.primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38BDF8, stop:1 #0EA5E9);
    color: #0F172A;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-size: 15px;
}
QPushButton.primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7DD3FC, stop:1 #38BDF8);
}
QPushButton.primary:disabled {
    background: #1E293B;
    color: #475569;
}
QPushButton.secondary {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton.secondary:hover {
    background-color: #334155;
    color: #F8FAFC;
    border: 1px solid #475569;
}
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    background-color: #1E293B;
    border-radius: 8px;
    margin-bottom: 10px;
    padding: 18px;
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 500;
    border: 1px solid #1E293B;
}
QListWidget::item:hover {
    background-color: #27344D;
}
QListWidget::item:selected {
    background-color: #1E293B;
    border: 1px solid #38BDF8;
    color: #38BDF8;
}
#AppList {
    background-color: transparent;
}
#AppList::item {
    background-color: transparent;
    color: #CBD5E1;
    padding: 12px 15px;
    border-radius: 8px;
    margin: 4px 10px;
    font-size: 14px;
    font-weight: 500;
}
#AppList::item:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}
#AppList::item:selected {
    background-color: #1E293B;
    border-left: 4px solid #38BDF8;
    color: #38BDF8;
    border-radius: 4px;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QDialog {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 12px;
}
QMenu {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px;
}
QMenu::item {
    padding: 8px 25px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #38BDF8;
    color: #0F172A;
    font-weight: bold;
}
QCheckBox {
    font-size: 14px;
    color: #CBD5E1;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #334155;
    background-color: #1E293B;
}
QCheckBox::indicator:checked {
    background-color: #38BDF8;
    border: 1px solid #38BDF8;
}
"""

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(350, 200)
        self.setStyleSheet(STYLE_SHEET)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; color: #38BDF8; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.settings = load_settings()
        
        self.startup_check = QCheckBox("Start with Windows")
        self.startup_check.setChecked(self.settings.get("startup", False))
        layout.addWidget(self.startup_check)
        
        self.tray_check = QCheckBox("Minimize to system tray")
        self.tray_check.setChecked(self.settings.get("tray", True))
        layout.addWidget(self.tray_check)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self.save_and_close)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_and_close(self):
        self.settings["startup"] = self.startup_check.isChecked()
        self.settings["tray"] = self.tray_check.isChecked()
        save_settings(self.settings)
        set_startup(self.settings["startup"])
        self.accept()

class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(45)
        self.parent_window = parent
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        
        icon_label = QLabel("🛡️")
        icon_label.setStyleSheet("color: #38BDF8; font-size: 16px; margin-right: 5px;")
        layout.addWidget(icon_label)
        
        title_label = QLabel("OmniVault Secure")
        layout.addWidget(title_label)
        layout.addStretch()
        
        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("MinBtn")
        self.min_btn.setFixedSize(40, 30)
        self.min_btn.setToolTip("Minimize")
        self.min_btn.setAccessibleName("Minimize Window")
        self.min_btn.clicked.connect(self.parent_window.minimize_action)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setFixedSize(40, 30)
        self.close_btn.setToolTip("Close")
        self.close_btn.setAccessibleName("Close Window")
        self.close_btn.clicked.connect(self.parent_window.close_action)
        
        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)
        
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.start_pos:
            self.parent_window.move(event.globalPosition().toPoint() - self.start_pos)
            event.accept()

class LoginScreen(QWidget):
    login_success = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.failed_attempts = 0
        self.lockout_until = 0
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("🔐")
        icon.setStyleSheet("font-size: 50px; margin-bottom: 10px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        
        self.title = QLabel("Vault Login")
        self.title.setStyleSheet("font-size: 32px; color: #38BDF8; font-weight: 800; margin-bottom: 25px; letter-spacing: 1px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Master Password")
        self.pwd_input.setFixedWidth(320)
        self.pwd_input.setFixedHeight(50)
        self.pwd_input.returnPressed.connect(self.attempt_login)
        layout.addWidget(self.pwd_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(15)
        
        self.login_btn = QPushButton("Unlock Vault")
        self.login_btn.setProperty("class", "primary")
        self.login_btn.setFixedWidth(320)
        self.login_btn.setFixedHeight(50)
        self.login_btn.clicked.connect(self.attempt_login)
        
        # Add shadow to login button
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor("#0EA5E9"))
        shadow.setOffset(0, 4)
        self.login_btn.setGraphicsEffect(shadow)
        
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF4444; margin-top: 20px; font-size: 14px; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_lockout)
        self.timer.start(1000)

    def showEvent(self, event):
        super().showEvent(event)
        if os.path.exists("my_vault.bin"):
            self.title.setText("Vault Login")
            self.pwd_input.setPlaceholderText("Master Password")
            self.login_btn.setText("Unlock Vault")
        else:
            self.title.setText("Create New Vault")
            self.pwd_input.setPlaceholderText("Set Master Password")
            self.login_btn.setText("Initialize Vault")

    def attempt_login(self):
        if time.time() < self.lockout_until:
            return
            
        pwd = self.pwd_input.text()
        self.pwd_input.clear()
        
        if not pwd:
            return
            
        vault = IncrementalVault(pwd)
        success = vault.load()
        
        if success:
            self.failed_attempts = 0
            self.error_label.setText("")
            self.login_success.emit(vault)
        else:
            self.failed_attempts += 1
            penalty = min(math.pow(2, self.failed_attempts), 300)
            if self.failed_attempts > 2:
                self.lockout_until = time.time() + penalty
                self.update_lockout()
            else:
                self.error_label.setText("Invalid password.")

    def update_lockout(self):
        if time.time() < self.lockout_until:
            remaining = int(self.lockout_until - time.time())
            self.error_label.setText(f"Locked out. Try again in {remaining}s")
            self.login_btn.setEnabled(False)
            self.pwd_input.setEnabled(False)
            tooltip_msg = f"Locked out for {remaining}s due to failed attempts"
            self.login_btn.setToolTip(tooltip_msg)
            self.pwd_input.setToolTip(tooltip_msg)
        else:
            if self.lockout_until != 0:
                self.error_label.setText("")
                self.lockout_until = 0
            self.login_btn.setEnabled(True)
            self.pwd_input.setEnabled(True)
            self.login_btn.setToolTip("")
            self.pwd_input.setToolTip("")

class AccountDialog(QDialog):
    def __init__(self, parent=None, app_name="", acc_name="", username="", password="", riot_logic=False):
        super().__init__(parent)
        self.setWindowTitle("Account")
        self.setFixedSize(420, 340)
        self.setStyleSheet(STYLE_SHEET)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.old_app_name = app_name
        self.old_acc_name = acc_name
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Add / Edit Account")
        title.setStyleSheet("font-size: 20px; color: #38BDF8; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        form = QFormLayout()
        self.app_input = QLineEdit(app_name)
        self.acc_input = QLineEdit(acc_name)
        self.user_input = QLineEdit(username)
        self.pwd_input = QLineEdit(password)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.riot_check = QCheckBox("Use Omni Login (Auto-type)")
        self.riot_check.setChecked(riot_logic)
        
        form.addRow("App Name:", self.app_input)
        form.addRow("Account Name:", self.acc_input)
        form.addRow("Username:", self.user_input)
        form.addRow("Password:", self.pwd_input)
        form.addRow("", self.riot_check)
        
        layout.addLayout(form)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)

    def get_data(self):
        return {
            "app_name": self.app_input.text().strip(),
            "acc_name": self.acc_input.text().strip(),
            "username": self.user_input.text(),
            "password": self.pwd_input.text(),
            "riot_logic": self.riot_check.isChecked()
        }

class MainScreen(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault = None
        self.parent_window = parent
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.app_list = QListWidget()
        self.app_list.setObjectName("AppList")
        self.app_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.app_list.model().rowsMoved.connect(self.save_app_order)
        self.app_list.itemClicked.connect(self.on_app_clicked)
        self.app_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.app_list.customContextMenuRequested.connect(self.show_app_context_menu)
        sidebar_layout.addWidget(self.app_list)
        
        sidebar_layout.addSpacing(10)
        
        self.add_app_btn = QPushButton("➕ New Account")
        self.add_app_btn.setProperty("class", "secondary")
        self.add_app_btn.clicked.connect(self.add_account)
        sidebar_layout.addWidget(self.add_app_btn)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setProperty("class", "secondary")
        self.settings_btn.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.settings_btn)
        
        self.lock_btn = QPushButton("🔒 Lock Vault")
        self.lock_btn.setProperty("class", "secondary")
        self.lock_btn.clicked.connect(self.logout_requested.emit)
        sidebar_layout.addWidget(self.lock_btn)
        
        layout.addWidget(self.sidebar)
        
        self.content_area = QFrame()
        self.content_area.setObjectName("ContentArea")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search credentials...")
        self.search_input.textChanged.connect(self.filter_credentials)
        content_layout.addWidget(self.search_input)
        
        content_layout.addSpacing(15)
        
        self.cred_list = QListWidget()
        self.cred_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.cred_list.model().rowsMoved.connect(self.save_cred_order)
        self.cred_list.itemClicked.connect(self.on_item_clicked)
        self.cred_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.cred_list.customContextMenuRequested.connect(self.show_cred_context_menu)
        content_layout.addWidget(self.cred_list)
        
        layout.addWidget(self.content_area)
        
        self.current_app = None

    def get_category_icon(self, name):
        name = name.lower()
        if "riot" in name: return "🎮"
        if "epic" in name: return "🕹️"
        if "twitch" in name: return "🟣"
        if "icloud" in name: return "☁️"
        if "oracle" in name: return "🔴"
        if "steam" in name: return "💨"
        if "google" in name: return "📧"
        if "discord" in name: return "💬"
        if "microsoft" in name: return "🪟"
        if "social" in name: return "👥"
        if "work" in name: return "💼"
        if "personal" in name: return "👤"
        if "bank" in name or "finance" in name: return "💰"
        return "📁"

    def get_account_icon(self, category, name):
        category = category.lower()
        name = name.lower()
        # Specific account name icons
        if "gmail" in name or "google" in name: return "📧"
        if "outlook" in name or "hotmail" in name: return "📧"
        if "github" in name: return "🐙"
        if "linkedin" in name: return "🔗"
        if "twitter" in name or " x " in name: return "🐦"
        if "facebook" in name or "fb" in name: return "🔵"
        if "instagram" in name: return "📸"
        if "reddit" in name: return "🤖"
        
        # Fallback to category icon if appropriate
        if "riot" in category: return "🔫"
        if "epic" in category: return "🎮"
        if "twitch" in category: return "📺"
        if "icloud" in category: return "🍏"
        if "oracle" in category: return "🗄️"
        
        return "🔑"

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def set_vault(self, vault):
        self.vault = vault
        self.refresh_sidebar()
        
    def refresh_sidebar(self):
        self.app_list.clear()
        if not self.vault:
            return
            
        apps = self.vault.get_apps()
        for app in apps:
            icon = self.get_category_icon(app)
            item = QListWidgetItem(f"{icon} {app.upper()}")
            item.setData(Qt.ItemDataRole.UserRole, app)
            self.app_list.addItem(item)
            
        if apps:
            self.select_app(apps[0])
        else:
            self.current_app = None
            self.refresh_credentials()

    def select_app(self, app_name):
        self.current_app = app_name
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == app_name:
                self.app_list.setCurrentItem(item)
        self.refresh_credentials()

    def on_app_clicked(self, item):
        app_name = item.data(Qt.ItemDataRole.UserRole)
        self.select_app(app_name)
        
    def refresh_credentials(self):
        self.cred_list.clear()
        if not self.vault or not self.current_app:
            return
            
        accounts = self.vault.get_accounts(self.current_app)
        for acc in accounts:
            icon = self.get_account_icon(self.current_app, acc)
            item = QListWidgetItem(f"{icon} {acc}")
            item.setData(Qt.ItemDataRole.UserRole, acc)
            self.cred_list.addItem(item)
            
        self.filter_credentials(self.search_input.text())

    def filter_credentials(self, text):
        for i in range(self.cred_list.count()):
            item = self.cred_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def save_app_order(self, parent, start, end, destination, row):
        if not self.vault: return
        order = []
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            order.append(item.data(Qt.ItemDataRole.UserRole))
        self.vault.set_app_order(order)
        self.vault.save()

    def save_cred_order(self, parent, start, end, destination, row):
        if not self.vault or not self.current_app: return
        order = []
        for i in range(self.cred_list.count()):
            item = self.cred_list.item(i)
            order.append(item.data(Qt.ItemDataRole.UserRole))
        self.vault.set_account_order(self.current_app, order)
        self.vault.save()

    def add_account(self):
        dialog = AccountDialog(self, app_name=self.current_app or "")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["app_name"] and data["acc_name"]:
                self.vault.set_entry(data["app_name"], data["acc_name"], {
                    "username": data["username"],
                    "password": data["password"],
                    "riot_logic": data["riot_logic"]
                })
                self.vault.save()
                self.refresh_sidebar()
                self.select_app(data["app_name"])

    def show_app_context_menu(self, pos):
        item = self.app_list.itemAt(pos)
        if not item: return
        
        app_name = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu()
        rename_action = menu.addAction("Rename Category")
        delete_action = menu.addAction("Delete Category")
        
        action = menu.exec(self.app_list.mapToGlobal(pos))
        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, "Rename Category", "New Name:", text=app_name)
            if ok and new_name and new_name != app_name:
                if new_name in self.vault.data:
                    QMessageBox.warning(self, "Error", "Category already exists!")
                    return
                
                apps = self.vault.get_apps()
                if app_name in apps:
                    apps[apps.index(app_name)] = new_name
                    self.vault.set_app_order(apps)
                
                self.vault.data[new_name] = self.vault.data.pop(app_name)

                if "__metadata__" in self.vault.data and "acc_order" in self.vault.data["__metadata__"]:
                    if app_name in self.vault.data["__metadata__"]["acc_order"]:
                        self.vault.data["__metadata__"]["acc_order"][new_name] = self.vault.data["__metadata__"]["acc_order"].pop(app_name)
                
                self.vault.save()
                self.refresh_sidebar()
                self.select_app(new_name)
                
        elif action == delete_action:
            confirm = QMessageBox.question(self, "Delete Category", f"Delete '{app_name}' and all its accounts?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.vault.delete_app(app_name)
                self.vault.save()
                self.refresh_sidebar()

    def show_cred_context_menu(self, pos):
        item = self.cred_list.itemAt(pos)
        if not item: return
        
        acc_name = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu()
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.cred_list.mapToGlobal(pos))
        if action == edit_action:
            data = self.vault.get_entry(self.current_app, acc_name)
            if not data: return
            
            dialog = AccountDialog(self, app_name=self.current_app, acc_name=acc_name, 
                                   username=data.get("username", ""), password=data.get("password", ""), 
                                   riot_logic=data.get("riot_logic", False))
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if new_data["app_name"] and new_data["acc_name"]:
                    if dialog.old_app_name != new_data["app_name"] or dialog.old_acc_name != new_data["acc_name"]:
                        self.vault.delete_entry(dialog.old_app_name, dialog.old_acc_name)
                        
                    self.vault.set_entry(new_data["app_name"], new_data["acc_name"], {
                        "username": new_data["username"],
                        "password": new_data["password"],
                        "riot_logic": new_data["riot_logic"]
                    })
                    self.vault.save()
                    self.refresh_sidebar()
                    self.select_app(new_data["app_name"])
                    
        elif action == delete_action:
            confirm = QMessageBox.question(self, "Delete Account", f"Delete '{acc_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.vault.delete_entry(self.current_app, acc_name)
                self.vault.save()
                self.refresh_credentials()

    def on_item_clicked(self, item):
        acc_name = item.data(Qt.ItemDataRole.UserRole)
        data = self.vault.get_entry(self.current_app, acc_name)
        if not data: return
        
        # Hide the window immediately
        self.parent_window.hide()
        
        if data.get('riot_logic', False):
            # Bypass clipboard entirely for Omni Login
            threading.Thread(target=self._execute_login_thread, args=(data,), daemon=True).start()
        else:
            # Copy to clipboard and set a 30-second timeout to clear it
            username = data.get('username', '')
            password = data.get('password', '')
            clipboard_text = f"{username}:{password}" if username else password
            
            clipboard = QApplication.clipboard()
            clipboard.setText(clipboard_text)
            QTimer.singleShot(30000, clipboard.clear)

    def _execute_login_thread(self, data):
        username = data['username']
        password = data['password']
        
        while ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000:
            time.sleep(0.01)

        while not (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000):
            time.sleep(0.01)
        
        time.sleep(0.1)
        pyautogui.write(username, interval=0)
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.write(password, interval=0)
        time.sleep(0.1)
        pyautogui.press('enter')

class OmniVaultApp(QMainWindow):
    toggle_visibility_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(900, 600)
        
        # Apply drop shadow to the main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 180))
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainWidget")
        self.central_widget.setStyleSheet(STYLE_SHEET + "\n#MainWidget { border-radius: 12px; background-color: #0B1120; border: 1px solid #1E293B; }")
        self.central_widget.setGraphicsEffect(shadow)
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.login_screen = LoginScreen()
        self.main_screen = MainScreen(parent=self)
        
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.main_screen)
        
        self.login_screen.login_success.connect(self.on_login_success)
        self.main_screen.logout_requested.connect(self.lock_vault)
        
        self.idle_timeout_sec = 300
        self.last_activity = time.time()
        
        self.mouse_listener = mouse.Listener(on_move=self._on_activity, on_click=self._on_activity, on_scroll=self._on_activity)
        self.kb_listener = keyboard.Listener(on_press=self._on_activity)
        self.mouse_listener.start()
        self.kb_listener.start()
        
        # Base keybind to ctrl+p
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+p': self.on_global_hotkey
        })
        self.hotkey_listener.start()
        
        self.toggle_visibility_signal.connect(self.toggle_visibility)
        
        self.check_idle_timer = QTimer(self)
        self.check_idle_timer.timeout.connect(self.check_idle)
        self.check_idle_timer.start(1000)

        # Tray Icon setup
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("OmniVault Secure")
        if os.path.exists("vault_icon.ico"):
            self.tray_icon.setIcon(QIcon("vault_icon.ico"))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
            
        tray_menu = QMenu()
        show_action = QAction("Show OmniVault", self)
        show_action.triggered.connect(self.show_app)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        settings = load_settings()
        if settings.get("tray", True):
            self.tray_icon.show()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_app()

    def show_app(self):
        self.showNormal()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        self.raise_()
        self.activateWindow()

    def minimize_action(self):
        settings = load_settings()
        if settings.get("tray", True):
            self.hide()
        else:
            self.showMinimized()

    def close_action(self):
        settings = load_settings()
        if settings.get("tray", True):
            self.hide()
            self.tray_icon.showMessage("OmniVault", "Vault is still running in the background.", QSystemTrayIcon.MessageIcon.Information, 2000)
        else:
            QApplication.instance().quit()

    def _on_activity(self, *args, **kwargs):
        self.last_activity = time.time()

    def check_idle(self):
        if self.stacked_widget.currentIndex() == 1:
            if time.time() - self.last_activity > self.idle_timeout_sec:
                self.lock_vault()

    def on_global_hotkey(self):
        self.toggle_visibility_signal.emit()

    def toggle_visibility(self):
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.showNormal()
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            self.raise_()
            self.activateWindow()

    def on_login_success(self, vault):
        self.main_screen.set_vault(vault)
        self.stacked_widget.setCurrentWidget(self.main_screen)
        self.last_activity = time.time()

    def lock_vault(self):
        self.main_screen.set_vault(None)
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.login_screen.pwd_input.clear()

def main():
    # Set working directory to the location of the executable or script
    # to ensure relative paths for vault and settings work correctly
    # especially when started by Windows at boot
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as a script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(base_dir)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    settings = load_settings()
    window = OmniVaultApp()
    
    if settings.get("startup", False) and "--startup" in sys.argv:
        pass # Start hidden in tray
    else:
        window.show()
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
