import unittest
from unittest.mock import MagicMock, patch
import sys

class MockQWidget:
    def __init__(self, *args, **kwargs): pass
    def setWindowFlags(self, *args, **kwargs): pass
    def setAttribute(self, *args, **kwargs): pass
    def resize(self, *args, **kwargs): pass
    def show(self, *args, **kwargs): pass
    def hide(self, *args, **kwargs): pass

class MockQDialog(MockQWidget): pass
class MockQMainWindow(MockQWidget): pass
class MockQFrame(MockQWidget): pass
class MockQSystemTrayIcon: pass

mock_qtwidgets = MagicMock()
mock_qtwidgets.QWidget = MockQWidget
mock_qtwidgets.QMainWindow = MockQMainWindow
mock_qtwidgets.QDialog = MockQDialog
mock_qtwidgets.QFrame = MockQFrame
mock_qtwidgets.QApplication = MagicMock
mock_qtwidgets.QSystemTrayIcon = MockQSystemTrayIcon

sys.modules['PyQt6'] = MagicMock()
sys.modules['PyQt6.QtWidgets'] = mock_qtwidgets
sys.modules['PyQt6.QtCore'] = MagicMock()
sys.modules['PyQt6.QtGui'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['winreg'] = MagicMock()
sys.modules['vault'] = MagicMock()

import secure_switcher

class TestClipboardClear(unittest.TestCase):
    def setUp(self):
        pass

    @patch('secure_switcher.QApplication')
    @patch('secure_switcher.QTimer')
    @patch('secure_switcher.threading.Thread')
    def test_on_item_clicked_no_riot(self, mock_thread, mock_qtimer, mock_qapp):
        with patch.object(secure_switcher.MainScreen, '__init__', lambda self, parent=None, vault=None: None):
            app_list = secure_switcher.MainScreen()
            app_list.vault = MagicMock()
            app_list.vault.get_entry.return_value = {'password': 'secret_password', 'riot_logic': False}
            app_list.current_app = "App"
            app_list.parent_window = MagicMock()

            mock_item = MagicMock()
            mock_item.data.return_value = "Account"

            mock_cb = MagicMock()
            mock_qapp.clipboard.return_value = mock_cb

            app_list.on_item_clicked(mock_item)

            mock_cb.setText.assert_called_with('secret_password')
            mock_qtimer.singleShot.assert_called_with(30000, mock_cb.clear)
            mock_thread.assert_not_called()

    @patch('secure_switcher.QApplication')
    @patch('secure_switcher.QTimer')
    @patch('secure_switcher.threading.Thread')
    def test_on_item_clicked_riot_logic(self, mock_thread, mock_qtimer, mock_qapp):
        with patch.object(secure_switcher.MainScreen, '__init__', lambda self, parent=None, vault=None: None):
            app_list = secure_switcher.MainScreen()
            app_list.vault = MagicMock()
            app_list.vault.get_entry.return_value = {'password': 'secret_password', 'username': 'user', 'riot_logic': True}
            app_list.current_app = "App"
            app_list.parent_window = MagicMock()

            mock_item = MagicMock()
            mock_item.data.return_value = "Account"

            mock_cb = MagicMock()
            mock_qapp.clipboard.return_value = mock_cb

            app_list.on_item_clicked(mock_item)

            mock_cb.setText.assert_not_called()
            mock_qtimer.singleShot.assert_not_called()
            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()

if __name__ == '__main__':
    unittest.main()
