from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QSlider, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.utils.password_utils import PasswordGenerator
from src.utils.clipboard import ClipboardHelper


class PasswordGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎲 Generate Password")
        self.setFixedSize(450, 450)
        self.generated_password = ""

        self._init_ui()
        self._generate_password()  # Generate initial password

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Generate Secure Password")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Length slider
        length_group = QGroupBox("Password Length")
        length_layout = QVBoxLayout()

        slider_layout = QHBoxLayout()
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(32)
        self.length_slider.setValue(16)
        self.length_slider.setTickPosition(QSlider.TicksBelow)
        self.length_slider.setTickInterval(4)
        self.length_slider.valueChanged.connect(self._on_length_changed)

        self.length_label = QLabel("16")
        self.length_label.setMinimumWidth(30)
        self.length_label.setAlignment(Qt.AlignCenter)
        length_font = QFont()
        length_font.setPointSize(14)
        length_font.setBold(True)
        self.length_label.setFont(length_font)

        slider_layout.addWidget(self.length_slider)
        slider_layout.addWidget(self.length_label)

        length_layout.addLayout(slider_layout)
        length_group.setLayout(length_layout)
        layout.addWidget(length_group)

        # Character type options
        options_group = QGroupBox("Character Types")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)

        self.check_uppercase = QCheckBox("Uppercase Letters (A-Z)")
        self.check_uppercase.setChecked(True)
        self.check_uppercase.toggled.connect(self._generate_password)

        self.check_lowercase = QCheckBox("Lowercase Letters (a-z)")
        self.check_lowercase.setChecked(True)
        self.check_lowercase.toggled.connect(self._generate_password)

        self.check_numbers = QCheckBox("Numbers (0-9)")
        self.check_numbers.setChecked(True)
        self.check_numbers.toggled.connect(self._generate_password)

        self.check_symbols = QCheckBox("Symbols (!@#$%^&*...)")
        self.check_symbols.setChecked(True)
        self.check_symbols.toggled.connect(self._generate_password)

        options_layout.addWidget(self.check_uppercase)
        options_layout.addWidget(self.check_lowercase)
        options_layout.addWidget(self.check_numbers)
        options_layout.addWidget(self.check_symbols)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Generated password display
        password_group = QGroupBox("Generated Password")
        password_layout = QVBoxLayout()

        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setMinimumHeight(50)
        password_font = QFont("Courier New")
        password_font.setPointSize(14)
        self.password_display.setFont(password_font)
        self.password_display.setAlignment(Qt.AlignCenter)

        password_layout.addWidget(self.password_display)
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)

        # Action buttons (Regenerate, Copy)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        btn_regenerate = QPushButton("🔄 Regenerate")
        btn_regenerate.setMinimumHeight(40)
        btn_regenerate.setObjectName("secondaryBtn")
        btn_regenerate.clicked.connect(self._generate_password)

        btn_copy = QPushButton("📋 Copy")
        btn_copy.setMinimumHeight(40)
        btn_copy.setObjectName("secondaryBtn")
        btn_copy.clicked.connect(self._copy_password)

        action_layout.addWidget(btn_regenerate)
        action_layout.addWidget(btn_copy)

        layout.addLayout(action_layout)

        layout.addStretch()

        # Dialog buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setObjectName("secondaryBtn")
        btn_cancel.clicked.connect(self.reject)

        btn_use = QPushButton("Use This Password")
        btn_use.setMinimumHeight(40)
        btn_use.setObjectName("primaryBtn")
        btn_use.clicked.connect(self.accept)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_use)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _on_length_changed(self, value):
        """Update length label and regenerate password"""
        self.length_label.setText(str(value))
        self._generate_password()

    def _generate_password(self):
        """Generate a new password based on current settings"""
        # Ensure at least one option is checked
        if not any([
            self.check_uppercase.isChecked(),
            self.check_lowercase.isChecked(),
            self.check_numbers.isChecked(),
            self.check_symbols.isChecked()
        ]):
            # Re-check lowercase if nothing is selected
            self.check_lowercase.setChecked(True)
            return

        length = self.length_slider.value()
        password = PasswordGenerator.generate(
            length=length,
            use_uppercase=self.check_uppercase.isChecked(),
            use_lowercase=self.check_lowercase.isChecked(),
            use_numbers=self.check_numbers.isChecked(),
            use_symbols=self.check_symbols.isChecked()
        )

        self.generated_password = password
        self.password_display.setText(password)

    def _copy_password(self):
        """Copy password to clipboard"""
        if self.generated_password:
            ClipboardHelper.copy_with_timeout(self.generated_password, 10000)
            # Could show a toast notification here

    def get_password(self):
        """Return the generated password"""
        return self.generated_password
