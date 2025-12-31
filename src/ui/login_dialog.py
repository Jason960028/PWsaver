from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QProgressBar, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from src.utils.password_utils import PasswordStrengthChecker


class LoginDialog(QDialog):
    password_accepted = Signal(str)

    def __init__(self, is_setup: bool = False, parent=None):
        super().__init__(parent)
        self.is_setup = is_setup
        self.setWindowTitle("🔒 PwKeeper - " + ("Setup" if is_setup else "Login"))
        self.setFixedSize(400, 300 if is_setup else 220)
        self.verified_password = None
        self.password_visible = False

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)

        # Logo/Icon at top
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # Title
        title = QLabel("Password Keeper" if not self.is_setup else "Setup Password Keeper")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Instructions
        if self.is_setup:
            instruction = QLabel("Set your Master Password\n(Do not lose this! It cannot be recovered.)")
            instruction.setAlignment(Qt.AlignCenter)
            instruction.setObjectName("captionLabel")
            instruction.setWordWrap(True)
        else:
            instruction = QLabel("Enter your Master Password")
            instruction.setAlignment(Qt.AlignCenter)
            instruction.setObjectName("subtitleLabel")

        layout.addWidget(instruction)

        layout.addSpacing(8)

        # Password field with show/hide toggle
        pwd_container = QHBoxLayout()
        self.input_pwd = QLineEdit()
        self.input_pwd.setEchoMode(QLineEdit.Password)
        self.input_pwd.setPlaceholderText("Master Password")
        self.input_pwd.setMinimumHeight(40)

        if self.is_setup:
            self.input_pwd.textChanged.connect(self._update_strength)

        pwd_container.addWidget(self.input_pwd)

        # Eye icon toggle button
        self.toggle_btn = QToolButton()
        self.toggle_btn.setText("👁")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setObjectName("iconBtn")
        self.toggle_btn.clicked.connect(self._toggle_password_visibility)
        pwd_container.addWidget(self.toggle_btn)

        layout.addLayout(pwd_container)

        # Confirm password (setup mode only)
        if self.is_setup:
            confirm_container = QHBoxLayout()
            self.input_confirm = QLineEdit()
            self.input_confirm.setEchoMode(QLineEdit.Password)
            self.input_confirm.setPlaceholderText("Confirm Password")
            self.input_confirm.setMinimumHeight(40)
            confirm_container.addWidget(self.input_confirm)

            # Eye icon for confirm field
            self.toggle_confirm_btn = QToolButton()
            self.toggle_confirm_btn.setText("👁")
            self.toggle_confirm_btn.setFixedSize(40, 40)
            self.toggle_confirm_btn.setCursor(Qt.PointingHandCursor)
            self.toggle_confirm_btn.setObjectName("iconBtn")
            self.toggle_confirm_btn.clicked.connect(self._toggle_confirm_visibility)
            confirm_container.addWidget(self.toggle_confirm_btn)

            layout.addLayout(confirm_container)

            # Password strength meter
            strength_layout = QVBoxLayout()
            strength_layout.setSpacing(4)

            self.strength_bar = QProgressBar()
            self.strength_bar.setMaximum(100)
            self.strength_bar.setValue(0)
            self.strength_bar.setTextVisible(False)
            self.strength_bar.setFixedHeight(8)
            self.strength_bar.setObjectName("strengthWeak")

            self.strength_label = QLabel("Password Strength: Weak")
            self.strength_label.setObjectName("captionLabel")
            self.strength_label.setAlignment(Qt.AlignCenter)

            strength_layout.addWidget(self.strength_bar)
            strength_layout.addWidget(self.strength_label)

            layout.addLayout(strength_layout)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setObjectName("secondaryBtn")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("OK")
        btn_ok.setMinimumHeight(40)
        btn_ok.setObjectName("primaryBtn")
        btn_ok.clicked.connect(self.on_ok)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Focus on password field
        self.input_pwd.setFocus()

    def _toggle_password_visibility(self):
        """Toggle password visibility"""
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.input_pwd.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.input_pwd.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁")

    def _toggle_confirm_visibility(self):
        """Toggle confirm password visibility"""
        if self.input_confirm.echoMode() == QLineEdit.Password:
            self.input_confirm.setEchoMode(QLineEdit.Normal)
            self.toggle_confirm_btn.setText("🙈")
        else:
            self.input_confirm.setEchoMode(QLineEdit.Password)
            self.toggle_confirm_btn.setText("👁")

    def _update_strength(self, password):
        """Update password strength meter"""
        if not self.is_setup:
            return

        strength, score, suggestions = PasswordStrengthChecker.check_strength(password)

        # Update progress bar
        self.strength_bar.setValue(score)

        # Update color based on strength
        if strength == 'weak':
            self.strength_bar.setObjectName("strengthWeak")
        elif strength == 'medium':
            self.strength_bar.setObjectName("strengthMedium")
        else:
            self.strength_bar.setObjectName("strengthStrong")

        # Force style update
        self.strength_bar.style().unpolish(self.strength_bar)
        self.strength_bar.style().polish(self.strength_bar)

        # Update label
        strength_text = PasswordStrengthChecker.get_strength_text(strength)
        self.strength_label.setText(f"Password Strength: {strength_text}")

    def on_ok(self):
        pwd = self.input_pwd.text()
        if not pwd:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return

        if self.is_setup:
            confirm = self.input_confirm.text()
            if pwd != confirm:
                QMessageBox.warning(self, "Error", "Passwords do not match.")
                return

            # Check password strength
            strength, score, suggestions = PasswordStrengthChecker.check_strength(pwd)
            if strength == 'weak':
                result = QMessageBox.question(
                    self,
                    "Weak Password",
                    f"Your password is weak (score: {score}/100).\n\nSuggestions:\n" +
                    "\n".join(f"• {s}" for s in suggestions) +
                    "\n\nDo you want to use it anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if result == QMessageBox.No:
                    return

        self.verified_password = pwd
        self.password_accepted.emit(pwd)
        self.accept()
