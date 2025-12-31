from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QToolButton,
    QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt
from src.ui.password_generator_dialog import PasswordGeneratorDialog
from src.utils.password_utils import PasswordStrengthChecker


class CredentialDialog(QDialog):
    def __init__(self, parent=None, cred_data=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ " + ("Edit Credential" if cred_data else "Add Credential"))
        self.setMinimumSize(500, 550)

        # Initialize with existing data if editing
        if cred_data:
            # cred_data: (id, category, site, user, enc_pass, is_favorite, url, notes)
            self.cred_id = cred_data[0]
            self.category = cred_data[1]
            self.site_name = cred_data[2]
            self.username = cred_data[3]
            self.password = ""  # Will be decrypted externally if needed
            self.url = cred_data[6] if len(cred_data) > 6 else ""
            self.notes = cred_data[7] if len(cred_data) > 7 else ""
        else:
            self.cred_id = None
            self.category = "General"
            self.site_name = ""
            self.username = ""
            self.password = ""
            self.url = ""
            self.notes = ""

        self.password_visible = False

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Edit Credential" if self.cred_id else "Add New Credential")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Category
        self.category_input = QComboBox()
        self.category_input.addItems(["General", "Social", "Work", "Finance", "Entertainment"])
        self.category_input.setCurrentText(self.category)
        self.category_input.setMinimumHeight(40)
        form_layout.addRow("Category:", self.category_input)

        # Site Name
        self.site_input = QLineEdit(self.site_name)
        self.site_input.setPlaceholderText("e.g., Facebook, Gmail")
        self.site_input.setMinimumHeight(40)
        form_layout.addRow("Site Name:*", self.site_input)

        # Username
        self.user_input = QLineEdit(self.username)
        self.user_input.setPlaceholderText("e.g., john@example.com")
        self.user_input.setMinimumHeight(40)
        form_layout.addRow("Username:*", self.user_input)

        # URL (optional)
        self.url_input = QLineEdit(self.url)
        self.url_input.setPlaceholderText("e.g., https://example.com")
        self.url_input.setMinimumHeight(40)
        form_layout.addRow("URL:", self.url_input)

        # Password with show/hide toggle and generator
        password_container = QHBoxLayout()
        password_container.setSpacing(8)

        self.pass_input = QLineEdit(self.password)
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Enter password")
        self.pass_input.setMinimumHeight(40)
        self.pass_input.textChanged.connect(self._update_strength)
        password_container.addWidget(self.pass_input, 1)

        # Show/Hide toggle
        self.toggle_btn = QToolButton()
        self.toggle_btn.setText("👁")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setObjectName("iconBtn")
        self.toggle_btn.setToolTip("Show/Hide Password")
        self.toggle_btn.clicked.connect(self._toggle_password_visibility)
        password_container.addWidget(self.toggle_btn)

        # Generator button
        btn_generate = QToolButton()
        btn_generate.setText("🎲")
        btn_generate.setFixedSize(40, 40)
        btn_generate.setCursor(Qt.PointingHandCursor)
        btn_generate.setObjectName("iconBtn")
        btn_generate.setToolTip("Generate Password")
        btn_generate.clicked.connect(self._open_generator)
        password_container.addWidget(btn_generate)

        form_layout.addRow("Password:*", password_container)

        # Password strength meter
        strength_layout = QVBoxLayout()
        strength_layout.setSpacing(4)

        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(8)
        self.strength_bar.setObjectName("strengthWeak")

        self.strength_label = QLabel("Strength: Weak")
        self.strength_label.setObjectName("captionLabel")

        strength_layout.addWidget(self.strength_bar)
        strength_layout.addWidget(self.strength_label)

        form_layout.addRow("", strength_layout)

        # Notes (optional)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes about this credential")
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setText(self.notes)
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

        # Required fields note
        required_note = QLabel("* Required fields")
        required_note.setObjectName("captionLabel")
        layout.addWidget(required_note)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setObjectName("secondaryBtn")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save")
        btn_save.setMinimumHeight(40)
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._on_save)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Trigger initial strength check if password exists
        if self.password:
            self._update_strength(self.password)

    def _toggle_password_visibility(self):
        """Toggle password visibility"""
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁")

    def _open_generator(self):
        """Open password generator dialog"""
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec():
            generated_password = dialog.get_password()
            if generated_password:
                self.pass_input.setText(generated_password)
                # Show the generated password temporarily
                self.pass_input.setEchoMode(QLineEdit.Normal)
                self.toggle_btn.setText("🙈")
                self.password_visible = True

    def _update_strength(self, password):
        """Update password strength meter"""
        if not password:
            self.strength_bar.setValue(0)
            self.strength_bar.setObjectName("strengthWeak")
            self.strength_label.setText("Strength: Weak")
            self.strength_bar.style().unpolish(self.strength_bar)
            self.strength_bar.style().polish(self.strength_bar)
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
        self.strength_label.setText(f"Strength: {strength_text} ({score}/100)")

    def _on_save(self):
        """Validate and save"""
        # Validate required fields
        site = self.site_input.text().strip()
        user = self.user_input.text().strip()
        pwd = self.pass_input.text()

        if not site:
            QMessageBox.warning(self, "Validation Error", "Site Name is required!")
            self.site_input.setFocus()
            return

        if not user:
            QMessageBox.warning(self, "Validation Error", "Username is required!")
            self.user_input.setFocus()
            return

        if not pwd:
            QMessageBox.warning(self, "Validation Error", "Password is required!")
            self.pass_input.setFocus()
            return

        # Warn about weak passwords
        strength, score, suggestions = PasswordStrengthChecker.check_strength(pwd)
        if strength == 'weak':
            result = QMessageBox.question(
                self,
                "Weak Password",
                f"This password is weak (score: {score}/100).\n\nContinue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if result == QMessageBox.No:
                return

        self.accept()

    def get_data(self):
        """Return form data as tuple"""
        return (
            self.category_input.currentText(),
            self.site_input.text().strip(),
            self.user_input.text().strip(),
            self.pass_input.text(),
            self.url_input.text().strip(),
            self.notes_input.toPlainText().strip()
        )

    def set_password(self, password):
        """Set password (used when editing existing credential)"""
        self.password = password
        self.pass_input.setText(password)
        self._update_strength(password)
