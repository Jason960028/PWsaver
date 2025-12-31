import sys
import os
import base64
from PySide6.QtWidgets import QApplication, QMessageBox
from src.core.db_manager import DBManager
from src.core.crypto_manager import CryptoManager
from src.ui.login_dialog import LoginDialog
from src.ui.main_window import MainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)

    # Note: Styles are now applied dynamically by ThemeManager in MainWindow

    # 1. Init Database
    db = DBManager()
    
    # 2. Check if Setup is required
    master_salt_hex = db.get_setting("master_salt")
    verifier = db.get_setting("verifier")
    
    encryption_key = None
    
    if not master_salt_hex or not verifier:
        # --- First Run Setup ---
        dialog = LoginDialog(is_setup=True)
        if dialog.exec() == LoginDialog.Accepted:
            password = dialog.verified_password
            
            # Generate Salt & Key
            salt = CryptoManager.generate_salt()
            key = CryptoManager.derive_key(password, salt)
            
            # Create Verifier
            # We encrypt a known string "VERIFIED" with the key.
            # If we can decrypt it later, the key is correct.
            ver_token = CryptoManager.encrypt_data("VERIFIED", key)
            
            # Store Salt and Verifier
            # Salt is bytes, store as Hex or Base64
            db.set_setting("master_salt", salt.hex())
            db.set_setting("verifier", ver_token.decode('utf-8')) # Store as string
            
            encryption_key = key
        else:
            sys.exit(0) # User cancelled setup
            
    else:
        # --- Login Flow ---
        salt = bytes.fromhex(master_salt_hex)
        
        while True:
            dialog = LoginDialog(is_setup=False)
            if dialog.exec() == LoginDialog.Accepted:
                password = dialog.verified_password
                
                # Derive key
                key_candidate = CryptoManager.derive_key(password, salt)
                
                # Verify
                try:
                    ver_token_bytes = verifier.encode('utf-8')
                    decrypted = CryptoManager.decrypt_data(ver_token_bytes, key_candidate)
                    
                    if decrypted == "VERIFIED":
                        encryption_key = key_candidate
                        break # Success
                    else:
                        # Should unlikely happen if decrypt succeeds but wrong text
                        QMessageBox.critical(None, "Error", "Integrity check failed.")
                except Exception:
                    # Decryption failed -> Wrong Password
                    QMessageBox.warning(None, "Login Failed", "Incorrect Password.")
            else:
                sys.exit(0) # User cancelled login

    # 3. Launch Main Window
    window = MainWindow(db, encryption_key)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
