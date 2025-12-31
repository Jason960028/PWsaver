from functools import partial
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QUrl, QTimer
from PySide6.QtGui import QFont, QDesktopServices, QCursor
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

        # Dynamic sizing
        self.setMinimumHeight(160)
        self.setMinimumWidth(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 16, 20, 16)

        # Top row: Category icon + Site name + Favorite button
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # Category badge (icon + label)
        category_container = QHBoxLayout()
        category_container.setSpacing(4)

        category_icons = {
            'General': '📋',
            'Social': '👥',
            'Work': '💼',
            'Finance': '💰',
            'Entertainment': '🎮'
        }

        icon_label = QLabel(category_icons.get(self.category, '📋'))
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        category_container.addWidget(icon_label)

        # Category name badge
        category_badge = QLabel(self.category)
        category_badge.setObjectName("categoryBadge")
        category_badge_font = QFont()
        category_badge_font.setPointSize(20)
        category_badge.setFont(category_badge_font)
        category_container.addWidget(category_badge)
        category_container.addStretch()

        top_layout.addLayout(category_container, 1)

        # Favorite button
        self.favorite_btn = QPushButton("⭐" if self.is_favorite else "☆")
        self.favorite_btn.setObjectName("iconBtn")
        self.favorite_btn.setFixedSize(36, 36)
        self.favorite_btn.setCursor(Qt.PointingHandCursor)
        self.favorite_btn.setToolTip("Toggle Favorite")
        self.favorite_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.cred_id))
        top_layout.addWidget(self.favorite_btn)

        layout.addLayout(top_layout)

        # Site name (prominent)
        site_label = QLabel(self.site_name)
        site_label.setObjectName("cardTitle")
        site_font = QFont()
        site_font.setPointSize(18)
        site_font.setBold(True)
        site_label.setFont(site_font)
        site_label.setWordWrap(False)
        # Enable text elision
        site_label.setTextFormat(Qt.PlainText)
        layout.addWidget(site_label)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setObjectName("cardDivider")
        layout.addWidget(divider)

        # Username with icon
        username_container = QHBoxLayout()
        username_container.setSpacing(6)
        username_icon = QLabel("👤")
        username_icon_font = QFont()
        username_icon_font.setPointSize(12)
        username_icon.setFont(username_icon_font)
        username_container.addWidget(username_icon)

        username_label = QLabel(self.username)
        username_label.setObjectName("cardUsername")
        username_label.setWordWrap(False)
        username_label_font = QFont()
        username_label_font.setPointSize(11)
        username_label.setFont(username_label_font)
        username_container.addWidget(username_label, 1)
        username_container.addStretch()

        layout.addLayout(username_container)

        # URL (if exists) - make it clickable
        if self.url:
            url_container = QHBoxLayout()
            url_container.setSpacing(6)
            url_icon = QLabel("🌐")
            url_icon_font = QFont()
            url_icon_font.setPointSize(12)
            url_icon.setFont(url_icon_font)
            url_container.addWidget(url_icon)

            self.url_label = QLabel(self._truncate_url(self.url, 35))
            self.url_label.setObjectName("cardUrl")
            self.url_label.setWordWrap(False)
            self.url_label.setCursor(Qt.PointingHandCursor)
            self.url_label.setToolTip(f"Click to open: {self.url}")
            self.url_label.mousePressEvent = lambda event: self._open_url()
            url_label_font = QFont()
            url_label_font.setPointSize(10)
            self.url_label.setFont(url_label_font)
            url_container.addWidget(self.url_label, 1)
            url_container.addStretch()

            layout.addLayout(url_container)

        # Notes preview (if exists)
        if self.notes:
            notes_container = QHBoxLayout()
            notes_container.setSpacing(6)
            notes_icon = QLabel("📝")
            notes_icon_font = QFont()
            notes_icon_font.setPointSize(12)
            notes_icon.setFont(notes_icon_font)
            notes_container.addWidget(notes_icon)

            notes_preview = self.notes[:40] + "..." if len(self.notes) > 40 else self.notes
            notes_label = QLabel(notes_preview)
            notes_label.setObjectName("cardNotes")
            notes_label.setWordWrap(True)
            notes_label.setMaximumHeight(40)
            notes_label_font = QFont()
            notes_label_font.setPointSize(9)
            notes_label.setFont(notes_label_font)
            notes_container.addWidget(notes_label, 1)

            layout.addLayout(notes_container)

        layout.addStretch()

        # Bottom row: Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        btn_copy = QPushButton("📋 Copy")
        btn_copy.setObjectName("cardActionBtn")
        btn_copy.setMinimumHeight(36)
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.setToolTip("Copy Password to Clipboard")
        btn_copy.clicked.connect(lambda: self.copy_clicked.emit(self.encrypted_password))

        btn_edit = QPushButton("✏️ Edit")
        btn_edit.setObjectName("cardActionBtn")
        btn_edit.setMinimumHeight(36)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Edit Credential")
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.cred_id))

        btn_delete = QPushButton("🗑️")
        btn_delete.setObjectName("dangerBtn")
        btn_delete.setFixedSize(36, 36)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Delete Credential")
        btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.cred_id))

        action_layout.addWidget(btn_copy, 1)
        action_layout.addWidget(btn_edit, 1)
        action_layout.addWidget(btn_delete)

        layout.addLayout(action_layout)

        self.setLayout(layout)

    def _truncate_url(self, url, max_length):
        """Truncate URL intelligently"""
        if len(url) <= max_length:
            return url

        # Try to keep the domain visible
        if url.startswith('http://'):
            url = url[7:]
        elif url.startswith('https://'):
            url = url[8:]

        if len(url) > max_length:
            return url[:max_length-3] + "..."
        return url

    def _open_url(self):
        """Open URL in default browser"""
        if self.url:
            url = self.url if self.url.startswith(('http://', 'https://')) else 'https://' + self.url
            QDesktopServices.openUrl(QUrl(url))

    def update_favorite(self, is_favorite):
        """Update favorite button display"""
        self.is_favorite = is_favorite
        self.favorite_btn.setText("⭐" if is_favorite else "☆")

    def enterEvent(self, event):
        """Mouse enter - add subtle hover effect"""
        self.setLineWidth(2)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leave - remove hover effect"""
        self.setLineWidth(1)
        super().leaveEvent(event)


class CardViewWidget(QWidget):
    """Container widget for displaying credentials as cards in a grid"""
    copy_password = Signal(str)  # encrypted_password
    edit_credential = Signal(int)  # cred_id
    delete_credential = Signal(int)  # cred_id
    toggle_favorite = Signal(int)  # cred_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self.current_data = []
        self.last_cards_per_row = 0
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._on_resize_complete)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container for cards
        self.card_container = QWidget()
        self.card_layout = QGridLayout()
        self.card_layout.setSpacing(20)
        self.card_layout.setContentsMargins(20, 20, 20, 20)

        # Make columns stretch equally
        self.card_layout.setColumnStretch(0, 1)
        self.card_layout.setColumnStretch(1, 1)
        self.card_layout.setColumnStretch(2, 1)
        self.card_layout.setColumnStretch(3, 1)

        self.card_container.setLayout(self.card_layout)

        self.scroll.setWidget(self.card_container)
        main_layout.addWidget(self.scroll)

        self.setLayout(main_layout)

    def set_data(self, credentials):
        """Populate cards with credential data"""
        # Store data for re-layout on resize
        self.current_data = credentials
        self._layout_cards()

    def _calculate_cards_per_row(self):
        """Calculate how many cards fit per row based on current width"""
        width = self.scroll.viewport().width()
        # Account for margins, spacing, and minimum card width
        min_card_width = 240
        margins_spacing = 40  # left + right margins
        card_spacing = 20

        # Calculate how many cards can fit
        available_width = width - margins_spacing

        if available_width < min_card_width:
            return 1

        # Calculate based on available space
        cards = 1
        while cards < 5:  # Max 5 columns
            total_width_needed = (min_card_width * (cards + 1)) + (card_spacing * cards)
            if total_width_needed > available_width:
                break
            cards += 1

        return max(1, cards)

    def _layout_cards(self):
        """Layout cards in grid based on current data"""
        # Calculate cards per row
        cards_per_row = self._calculate_cards_per_row()
        self.last_cards_per_row = cards_per_row

        # Clear existing cards
        self._clear_cards()

        if not self.current_data:
            # Show empty state
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignCenter)

            empty_icon = QLabel("📭")
            empty_icon_font = QFont()
            empty_icon_font.setPointSize(64)
            empty_icon.setFont(empty_icon_font)
            empty_icon.setAlignment(Qt.AlignCenter)

            empty_text = QLabel("No credentials found")
            empty_text.setAlignment(Qt.AlignCenter)
            empty_text.setObjectName("emptyStateTitle")
            empty_text_font = QFont()
            empty_text_font.setPointSize(18)
            empty_text_font.setBold(True)
            empty_text.setFont(empty_text_font)

            empty_hint = QLabel("Click '+ Add Credential' to create your first credential")
            empty_hint.setAlignment(Qt.AlignCenter)
            empty_hint.setObjectName("emptyStateHint")
            empty_hint_font = QFont()
            empty_hint_font.setPointSize(12)
            empty_hint.setFont(empty_hint_font)

            empty_layout.addStretch()
            empty_layout.addWidget(empty_icon)
            empty_layout.addSpacing(20)
            empty_layout.addWidget(empty_text)
            empty_layout.addSpacing(10)
            empty_layout.addWidget(empty_hint)
            empty_layout.addStretch()

            self.card_layout.addWidget(empty_widget, 0, 0, 1, cards_per_row)
            return

        # Update column stretch based on cards per row
        for i in range(5):
            if i < cards_per_row:
                self.card_layout.setColumnStretch(i, 1)
            else:
                self.card_layout.setColumnStretch(i, 0)

        # Create and add cards
        for i, cred_data in enumerate(self.current_data):
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
        total_rows = (len(self.current_data) - 1) // cards_per_row + 1
        self.card_layout.setRowStretch(total_rows, 1)

    def resizeEvent(self, event):
        """Handle resize events to adjust card layout"""
        super().resizeEvent(event)

        # Use timer to debounce resize events
        if self.current_data:
            self.resize_timer.start(150)  # Wait 150ms after last resize

    def _on_resize_complete(self):
        """Called when resize is complete (debounced)"""
        if not self.current_data:
            return

        # Only re-layout if cards per row changed
        new_cards_per_row = self._calculate_cards_per_row()
        if new_cards_per_row != self.last_cards_per_row:
            self._layout_cards()

    def _clear_cards(self):
        """Remove all cards from layout"""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()

        # Clear layout
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def clear_cards(self):
        """Public method to remove all cards"""
        self._clear_cards()
        self.current_data = []

    def update_favorite_status(self, cred_id, is_favorite):
        """Update favorite status for a specific card"""
        for card in self.cards:
            if card.cred_id == cred_id:
                card.update_favorite(is_favorite)
                break
