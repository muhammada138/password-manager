import sys
import time
import math
import os
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QStackedWidget, QFrame, QMessageBox, QDialog, QFormLayout, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from pynput import keyboard, mouse
import pyautogui
from vault import IncrementalVault

STYLE_SHEET = """
QMainWindow {
    background-color: #0F172A;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #F8FAFC;
}
#TitleBar {
    background-color: #1E293B;
}
#TitleBar QLabel {
    color: #38BDF8;
    font-weight: bold;
    font-size: 14px;
}
#TitleBar QPushButton {
    background-color: transparent;
    border: none;
    font-size: 16px;
    color: #94A3B8;
}
#TitleBar QPushButton:hover {
    background-color: #334155;
    color: #F8FAFC;
}
#TitleBar #CloseBtn:hover {
    background-color: #EF4444;
    color: #FFFFFF;
}
#Sidebar {
    background-color: #1E293B;
    border-right: 1px solid #334155;
}
#Sidebar QPushButton {
    background-color: transparent;
    text-align: left;
    padding: 12px 15px;
    border: none;
    border-radius: 6px;
    margin: 4px 10px;
    font-size: 13px;
}
#Sidebar QPushButton:hover {
    background-color: #334155;
}
#Sidebar QPushButton:checked {
    background-color: #38BDF8;
    color: #0F172A;
    font-weight: bold;
}
#ContentArea {
    background-color: #0F172A;
}
QLineEdit {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 10px;
    color: #F8FAFC;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #38BDF8;
}
QPushButton.primary {
    background-color: #38BDF8;
    color: #0F172A;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 12px;
    font-size: 14px;
}
QPushButton.primary:hover {
    background-color: #7DD3FC;
}
QPushButton.secondary {
    background-color: #334155;
    color: #F8FAFC;
    border: none;
    border-radius: 6px;
    padding: 12px;
    font-size: 13px;
}
QPushButton.secondary:hover {
    background-color: #475569;
}
QListWidget {
    background-color: #0F172A;
    border: none;
    outline: none;
}
QListWidget::item {
    background-color: #1E293B;
    border-radius: 6px;
    margin-bottom: 8px;
    padding: 15px;
}
QListWidget::item:selected {
    background-color: #334155;
    border: 1px solid #38BDF8;
}
QScrollBar:vertical {
    border: none;
    background: #0F172A;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 5px;
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
}
"""

class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(40)
        self.parent_window = parent
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        
        title_label = QLabel("OmniVault Secure")
        layout.addWidget(title_label)
        layout.addStretch()
        
        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("MinBtn")
        self.min_btn.setFixedSize(40, 30)
        self.min_btn.clicked.connect(self.parent_window.showMinimized)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setFixedSize(40, 30)
        self.close_btn.clicked.connect(self.parent_window.close)
        
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
        
        self.title = QLabel("Vault Login")
        self.title.setStyleSheet("font-size: 28px; color: #38BDF8; font-weight: bold; margin-bottom: 30px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Master Password")
        self.pwd_input.setFixedWidth(300)
        self.pwd_input.returnPressed.connect(self.attempt_login)
        layout.addWidget(self.pwd_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.login_btn = QPushButton("Unlock")
        self.login_btn.setProperty("class", "primary")
        self.login_btn.setFixedWidth(300)
        self.login_btn.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF4444; margin-top: 15px; font-size: 13px;")
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
            self.login_btn.setText("Unlock")
        else:
            self.title.setText("Create New Vault")
            self.pwd_input.setPlaceholderText("Set Master Password")
            self.login_btn.setText("Create Vault")

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
        else:
            if self.lockout_until != 0:
                self.error_label.setText("")
                self.lockout_until = 0
            self.login_btn.setEnabled(True)
            self.pwd_input.setEnabled(True)

class AccountDialog(QDialog):
    def __init__(self, parent=None, app_name="", acc_name="", username="", password="", riot_logic=False):
        super().__init__(parent)
        self.setWindowTitle("Account")
        self.setFixedSize(400, 300)
        self.setStyleSheet(STYLE_SHEET)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Add / Edit Account")
        title.setStyleSheet("font-size: 18px; color: #38BDF8; font-weight: bold;")
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
            "app_name": self.app_input.text(),
            "acc_name": self.acc_input.text(),
            "username": self.user_input.text(),
            "password": self.pwd_input.text(),
            "riot_logic": self.riot_check.isChecked()
        }

class MainScreen(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault = None
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.app_list = QVBoxLayout()
        self.app_list.setSpacing(0)
        sidebar_layout.addLayout(self.app_list)
        
        sidebar_layout.addStretch()
        
        self.add_app_btn = QPushButton("+ New Account")
        self.add_app_btn.setProperty("class", "secondary")
        self.add_app_btn.clicked.connect(self.add_account)
        sidebar_layout.addWidget(self.add_app_btn)
        
        self.lock_btn = QPushButton("Lock Vault")
        self.lock_btn.setProperty("class", "secondary")
        self.lock_btn.clicked.connect(self.logout_requested.emit)
        sidebar_layout.addWidget(self.lock_btn)
        
        layout.addWidget(self.sidebar)
        
        self.content_area = QFrame()
        self.content_area.setObjectName("ContentArea")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search credentials...")
        self.search_input.textChanged.connect(self.filter_credentials)
        content_layout.addWidget(self.search_input)
        
        self.cred_list = QListWidget()
        self.cred_list.itemClicked.connect(self.on_item_clicked)
        content_layout.addWidget(self.cred_list)
        
        layout.addWidget(self.content_area)
        
        self.current_app = None

    def set_vault(self, vault):
        self.vault = vault
        self.refresh_sidebar()
        
    def refresh_sidebar(self):
        for i in reversed(range(self.app_list.count())): 
            widget = self.app_list.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        if not self.vault:
            return
            
        apps = self.vault.get_apps()
        for app in apps:
            btn = QPushButton(app.upper())
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, a=app: self.select_app(a))
            self.app_list.addWidget(btn)
            
        if apps:
            self.select_app(apps[0])
        else:
            self.current_app = None
            self.refresh_credentials()

    def select_app(self, app_name):
        self.current_app = app_name
        for i in range(self.app_list.count()):
            btn = self.app_list.itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(btn.text().lower() == app_name.lower())
                
        self.refresh_credentials()
        
    def refresh_credentials(self):
        self.cred_list.clear()
        if not self.vault or not self.current_app:
            return
            
        accounts = self.vault.get_accounts(self.current_app)
        for acc in accounts:
            item = QListWidgetItem(f"{acc}")
            item.setData(Qt.ItemDataRole.UserRole, acc)
            self.cred_list.addItem(item)
            
        self.filter_credentials(self.search_input.text())

    def filter_credentials(self, text):
        for i in range(self.cred_list.count()):
            item = self.cred_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

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

    def on_item_clicked(self, item):
        acc_name = item.data(Qt.ItemDataRole.UserRole)
        data = self.vault.get_entry(self.current_app, acc_name)
        if not data: return
        
        QApplication.clipboard().setText(data['password'])
        
        if data.get('riot_logic', False):
            threading.Thread(target=self._execute_login_thread, args=(data,), daemon=True).start()
        else:
            QMessageBox.information(self, "Copied", f"Password for {acc_name} copied to clipboard!")

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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(850, 550)
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainWidget")
        self.central_widget.setStyleSheet(STYLE_SHEET + "\n#MainWidget { border-radius: 8px; background-color: #0F172A; border: 1px solid #334155; }")
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.login_screen = LoginScreen()
        self.main_screen = MainScreen()
        
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
        
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+v': self.on_global_hotkey
        })
        self.hotkey_listener.start()
        
        self.toggle_visibility_signal.connect(self.toggle_visibility)
        
        self.check_idle_timer = QTimer(self)
        self.check_idle_timer.timeout.connect(self.check_idle)
        self.check_idle_timer.start(1000)

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
    app = QApplication(sys.argv)
    window = OmniVaultApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
