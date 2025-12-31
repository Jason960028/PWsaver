from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

class ClipboardHelper:
    @staticmethod
    def copy_with_timeout(text: str, timeout_ms: int = 10000):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Determine if we can clear just this entry? 
        # Actually standard clipboard is global. We just clear it after N seconds.
        QTimer.singleShot(timeout_ms, lambda: clipboard.clear())
