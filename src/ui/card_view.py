from functools import partial
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from src.utils.password_utils import PasswordStrengthChecker


class CredentialCard(QFrame):
    """A single credential card widget"""
    copy_clicked = Signal(str)  # encrypted_password
    edit_clicked = Signal(int)  # cred_id
    delete_clicked = Signal(int)  # cred_id
    favorite_clicked = Signal(int)  # cred_id

    def __init__(self, cred_data, parent=None):
        super().__init__(parent)
        # cred_data: (id, category, site, user, enc_pass, is_favorite, url, notes)
        self.cred_id = cred_data[0]
        self.category = cred_data[1]
        self.site_name = cred_data[2]
        self.username = cred_data[3]
        self.encrypted_password = cred_data[4]
        self.is_favorite = cred_data[5] if len(cred_data) > 5 else 0
        self.url = cred_data[6] if len(cred_data) > 6 else ""
        self.notes = cred_data[7] if len(cred_data) > 7 else ""

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(1)
        self.setObjectName("credentialCard")
        self.setMinimumHeight(140)
        self.setMaximumHeight(180)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # Top row: Category icon + Site name + Favorite button
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        # Category icon
        category_icons = {
            'General': '📋',
            'Social': '👥',
            'Work': '💼',
            'Finance': '💰',
            'Entertainment': '🎮'
        }
        icon_label = QLabel(category_icons.get(self.category, '📋'))
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_label.setFont(icon_font)
        top_layout.addWidget(icon_label)

        # Site name
        site_label = QLabel(self.site_name)
        site_label.setObjectName("cardTitle")
        site_font = QFont()
        site_font.setPointSize(16)
        site_font.setBold(True)
        site_label.setFont(site_font)
        top_layout.addWidget(site_label, 1)

        # Favorite button
        self.favorite_btn = QPushButton("⭐" if self.is_favorite else "☆")
        self.favorite_btn.setObjectName("iconBtn")
        self.favorite_btn.setFixedSize(32, 32)
        self.favorite_btn.setCursor(Qt.PointingHandCursor)
        self.favorite_btn.setToolTip("Toggle Favorite")
        self.favorite_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.cred_id))
        top_layout.addWidget(self.favorite_btn)

        layout.addLayout(top_layout)

        # Username
        username_label = QLabel(f"👤 {self.username}")
        username_label.setObjectName("cardUsername")
        layout.addWidget(username_label)

        # URL (if exists)
        if self.url:
            url_label = QLabel(f"🌐 {self.url}")
            url_label.setObjectName("cardUrl")
            url_label.setWordWrap(True)
            layout.addWidget(url_label)

        # Notes preview (if exists)
        if self.notes:
            notes_preview = self.notes[:50] + "..." if len(self.notes) > 50 else self.notes
            notes_label = QLabel(f"📝 {notes_preview}")
            notes_label.setObjectName("cardNotes")
            notes_label.setWordWrap(True)
            layout.addWidget(notes_label)

        layout.addStretch()

        # Bottom row: Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        btn_copy = QPushButton("📋 Copy")
        btn_copy.setObjectName("cardActionBtn")
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.setToolTip("Copy Password")
        btn_copy.clicked.connect(lambda: self.copy_clicked.emit(self.encrypted_password))

        btn_edit = QPushButton("✏️ Edit")
        btn_edit.setObjectName("cardActionBtn")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Edit Credential")
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.cred_id))

        btn_delete = QPushButton("🗑️")
        btn_delete.setObjectName("dangerBtn")
        btn_delete.setFixedSize(32, 32)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Delete Credential")
        btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.cred_id))

        action_layout.addWidget(btn_copy)
        action_layout.addWidget(btn_edit)
        action_layout.addStretch()
        action_layout.addWidget(btn_delete)

        layout.addLayout(action_layout)

        self.setLayout(layout)

    def update_favorite(self, is_favorite):
        """Update favorite button display"""
        self.is_favorite = is_favorite
        self.favorite_btn.setText("⭐" if is_favorite else "☆")


class CardViewWidget(QWidget):
    """Container widget for displaying credentials as cards in a grid"""
    copy_password = Signal(str)  # encrypted_password
    edit_credential = Signal(int)  # cred_id
    delete_credential = Signal(int)  # cred_id
    toggle_favorite = Signal(int)  # cred_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        # Container for cards
        self.card_container = QWidget()
        self.card_layout = QGridLayout()
        self.card_layout.setSpacing(16)
        self.card_layout.setContentsMargins(16, 16, 16, 16)
        self.card_container.setLayout(self.card_layout)

        scroll.setWidget(self.card_container)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def set_data(self, credentials):
        """Populate cards with credential data"""
        # Clear existing cards
        self.clear_cards()

        if not credentials:
            # Show empty state
            empty_label = QLabel("No credentials found\n\nClick '+ Add' to create your first credential")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setObjectName("emptyState")
            self.card_layout.addWidget(empty_label, 0, 0, 1, 3)
            return

        # Calculate cards per row (responsive: 2-3 cards depending on width)
        cards_per_row = 3

        # Create and add cards
        for i, cred_data in enumerate(credentials):
            card = CredentialCard(cred_data, self)

            # Connect signals
            card.copy_clicked.connect(self.copy_password.emit)
            card.edit_clicked.connect(self.edit_credential.emit)
            card.delete_clicked.connect(self.delete_credential.emit)
            card.favorite_clicked.connect(self.toggle_favorite.emit)

            self.cards.append(card)

            # Add to grid
            row = i // cards_per_row
            col = i % cards_per_row
            self.card_layout.addWidget(card, row, col)

        # Add stretch to push cards to top
        self.card_layout.setRowStretch(len(credentials) // cards_per_row + 1, 1)

    def clear_cards(self):
        """Remove all cards"""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()

        # Clear layout
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_favorite_status(self, cred_id, is_favorite):
        """Update favorite status for a specific card"""
        for card in self.cards:
            if card.cred_id == cred_id:
                card.update_favorite(is_favorite)
                break
