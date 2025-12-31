from functools import partial
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QListWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QHeaderView, QMessageBox, QToolButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.ui.credential_dialog import CredentialDialog
from src.ui.card_view import CardViewWidget
from src.ui.theme_manager import ThemeManager, ICONS
from src.core.crypto_manager import CryptoManager
from src.utils.clipboard import ClipboardHelper


class MainWindow(QMainWindow):
    def __init__(self, db_manager, encryption_key):
        super().__init__()
        self.db_manager = db_manager
        self.encryption_key = encryption_key

        # Initialize theme manager
        saved_theme = self.db_manager.get_preference('theme', 'light')
        self.theme_manager = ThemeManager(saved_theme)

        # View mode (table or card)
        self.view_mode = self.db_manager.get_preference('view_mode', 'table')

        self.setWindowTitle("🔒 PwKeeper - Password Manager")
        self.resize(1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.apply_theme()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top header bar
        self._create_header_bar(main_layout)

        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)

        # Sidebar
        self._create_sidebar(content_layout)

        # Right side content
        self._create_content_area(content_layout)

        main_layout.addLayout(content_layout)

    def _create_header_bar(self, parent_layout):
        """Create top header bar with app title and theme toggle"""
        header = QWidget()
        header.setObjectName("headerBar")
        header.setFixedHeight(60)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # App title/logo
        title_layout = QHBoxLayout()
        title_icon = QLabel("🔒")
        title_icon_font = QFont()
        title_icon_font.setPointSize(24)
        title_icon.setFont(title_icon_font)

        title_label = QLabel("PwKeeper")
        title_label.setObjectName("titleLabel")

        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        header_layout.addLayout(title_layout)

        header_layout.addStretch()

        # View mode toggle
        self.view_toggle_btn = QToolButton()
        self.view_toggle_btn.setText("🗃️" if self.view_mode == 'table' else "📊")
        self.view_toggle_btn.setFixedSize(40, 40)
        self.view_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.view_toggle_btn.setObjectName("iconBtn")
        self.view_toggle_btn.setToolTip("Toggle View Mode")
        self.view_toggle_btn.clicked.connect(self.toggle_view_mode)
        header_layout.addWidget(self.view_toggle_btn)

        # Theme toggle button
        self.theme_toggle_btn = QToolButton()
        self.theme_toggle_btn.setText("🌙" if self.theme_manager.current_theme == 'light' else "☀️")
        self.theme_toggle_btn.setFixedSize(40, 40)
        self.theme_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.theme_toggle_btn.setObjectName("iconBtn")
        self.theme_toggle_btn.setToolTip("Toggle Dark/Light Mode")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_toggle_btn)

        parent_layout.addWidget(header)

    def _create_sidebar(self, parent_layout):
        """Create sidebar with category filters"""
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)

        # Add categories with icons
        categories = [
            f"{ICONS['all']} All",
            f"{ICONS['general']} General",
            f"{ICONS['social']} Social",
            f"{ICONS['work']} Work",
            f"{ICONS['finance']} Finance",
            f"{ICONS['entertainment']} Entertainment",
            "",  # Separator
            f"{ICONS['star']} Favorites"
        ]

        for cat in categories:
            self.sidebar.addItem(cat)

        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.filter_by_category)

        parent_layout.addWidget(self.sidebar)

    def _create_content_area(self, parent_layout):
        """Create main content area with search, actions, and data view"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(16)

        # Top bar (Search + Add)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        # Search with icon
        search_container = QHBoxLayout()
        search_container.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(f"{ICONS['search']} Search by site or username...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.search_table)
        search_container.addWidget(self.search_input)

        # Clear search button
        self.clear_search_btn = QToolButton()
        self.clear_search_btn.setText(ICONS['close'])
        self.clear_search_btn.setFixedSize(40, 40)
        self.clear_search_btn.setCursor(Qt.PointingHandCursor)
        self.clear_search_btn.setObjectName("iconBtn")
        self.clear_search_btn.setToolTip("Clear Search")
        self.clear_search_btn.clicked.connect(lambda: self.search_input.clear())
        self.clear_search_btn.setVisible(False)
        search_container.addWidget(self.clear_search_btn)

        # Show/hide clear button based on search text
        self.search_input.textChanged.connect(
            lambda text: self.clear_search_btn.setVisible(bool(text))
        )

        top_bar.addLayout(search_container)

        # Add button
        btn_add = QPushButton(f"{ICONS['add']} Add Credential")
        btn_add.setMinimumHeight(40)
        btn_add.setObjectName("primaryBtn")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.add_credential)
        top_bar.addWidget(btn_add)

        right_layout.addLayout(top_bar)

        # Stacked widget for table/card view
        self.view_stack = QStackedWidget()

        # Table view
        self._create_table_view()
        self.view_stack.addWidget(self.table)

        # Card view
        self.card_view = CardViewWidget()
        self.card_view.copy_password.connect(self.copy_password)
        self.card_view.edit_credential.connect(self.edit_credential)
        self.card_view.delete_credential.connect(self.delete_credential)
        self.card_view.toggle_favorite.connect(self.toggle_favorite)
        self.view_stack.addWidget(self.card_view)

        # Set initial view
        self.view_stack.setCurrentIndex(0 if self.view_mode == 'table' else 1)

        right_layout.addWidget(self.view_stack)

        parent_layout.addWidget(right_widget)

    def _create_table_view(self):
        """Create table view for credentials"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Category", "Site Name", "Username", "⭐", "Actions", ""])

        # Hide vertical header
        self.table.verticalHeader().setVisible(False)

        # Column resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Site
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Username
        header.setSectionResizeMode(3, QHeaderView.Fixed)             # Favorite
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions (auto-resize)
        header.setSectionResizeMode(5, QHeaderView.Fixed)             # Delete

        self.table.setColumnWidth(3, 50)   # Favorite column
        self.table.setColumnWidth(5, 50)   # Delete column

        # Selection behavior
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)

        # Row height
        self.table.verticalHeader().setDefaultSectionSize(50)

    def load_data(self):
        """Load credentials from database"""
        self.all_data = self.db_manager.get_all_credentials_extended()
        self.populate_views(self.all_data)

    def populate_views(self, data):
        """Populate both table and card views with data"""
        # Populate table view
        self.table.setRowCount(0)

        if not data:
            # Show empty state in table
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No credentials found. Click '+ Add Credential' to get started.")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 6)
        else:
            for i, row in enumerate(data):
                # row: (id, category, site, user, enc_pass, is_favorite, url, notes)
                cred_id, category, site, user, enc_pass = row[0], row[1], row[2], row[3], row[4]
                is_favorite = row[5] if len(row) > 5 else 0

                self.table.insertRow(i)

                # Category with icon
                category_icons = {
                    'General': '📋',
                    'Social': '👥',
                    'Work': '💼',
                    'Finance': '💰',
                    'Entertainment': '🎮'
                }
                cat_text = f"{category_icons.get(category, '📋')} {category}"
                cat_item = QTableWidgetItem(cat_text)
                self.table.setItem(i, 0, cat_item)

                # Site name
                self.table.setItem(i, 1, QTableWidgetItem(site))

                # Username
                self.table.setItem(i, 2, QTableWidgetItem(user))

                # Favorite button
                btn_favorite = QPushButton("⭐" if is_favorite else "☆")
                btn_favorite.setObjectName("iconBtn")
                btn_favorite.setCursor(Qt.PointingHandCursor)
                btn_favorite.setToolTip("Toggle Favorite")
                btn_favorite.clicked.connect(partial(self.toggle_favorite, cred_id))
                self.table.setCellWidget(i, 3, btn_favorite)

                # Action buttons container
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
                action_layout.setSpacing(2)  # Minimal spacing between buttons

                # Copy button
                btn_copy = QPushButton(f"{ICONS['copy']} Copy")
                btn_copy.setCursor(Qt.PointingHandCursor)
                btn_copy.setToolTip("Copy Password")
                btn_copy.clicked.connect(partial(self.copy_password, enc_pass))
                action_layout.addWidget(btn_copy)

                # Edit button
                btn_edit = QPushButton(f"{ICONS['edit']}")
                btn_edit.setObjectName("iconBtn")
                btn_edit.setCursor(Qt.PointingHandCursor)
                btn_edit.setToolTip("Edit Credential")
                btn_edit.clicked.connect(partial(self.edit_credential, cred_id))
                action_layout.addWidget(btn_edit)

                self.table.setCellWidget(i, 4, action_widget)

                # Delete button
                btn_delete = QPushButton(ICONS['delete'])
                btn_delete.setObjectName("dangerBtn")
                btn_delete.setCursor(Qt.PointingHandCursor)
                btn_delete.setToolTip("Delete Credential")
                btn_delete.clicked.connect(partial(self.delete_credential, cred_id))
                self.table.setCellWidget(i, 5, btn_delete)

        # Populate card view
        self.card_view.set_data(data)

    def add_credential(self):
        """Open dialog to add new credential"""
        dialog = CredentialDialog(self)
        if dialog.exec():
            cat, site, user, pwd, url, notes = dialog.get_data()
            if not site or not user or not pwd:
                QMessageBox.warning(self, "Error", "Site Name, Username, and Password are required!")
                return

            # Encrypt password
            try:
                encrypted = CryptoManager.encrypt_data(pwd, self.encryption_key)
                encrypted_str = encrypted.decode('utf-8')
                self.db_manager.add_credential_extended(cat, site, user, encrypted_str, url, notes)
                self.load_data()
                self.statusBar().showMessage(f"✓ Credential for '{site}' added successfully!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save credential: {str(e)}")

    def edit_credential(self, cred_id):
        """Edit existing credential"""
        cred_data = self.db_manager.get_credential_by_id_extended(cred_id)
        if not cred_data:
            QMessageBox.warning(self, "Error", "Credential not found!")
            return

        dialog = CredentialDialog(self, cred_data)

        # Decrypt and set password
        try:
            encrypted_bytes = cred_data[4].encode('utf-8')
            decrypted_pwd = CryptoManager.decrypt_data(encrypted_bytes, self.encryption_key)
            dialog.set_password(decrypted_pwd)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decrypt password: {str(e)}")
            return

        if dialog.exec():
            cat, site, user, pwd, url, notes = dialog.get_data()
            if not site or not user or not pwd:
                QMessageBox.warning(self, "Error", "Site Name, Username, and Password are required!")
                return

            # Encrypt password
            try:
                encrypted = CryptoManager.encrypt_data(pwd, self.encryption_key)
                encrypted_str = encrypted.decode('utf-8')
                self.db_manager.update_credential_extended(cred_id, cat, site, user, encrypted_str, url, notes)
                self.load_data()
                self.statusBar().showMessage(f"✓ Credential for '{site}' updated successfully!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update credential: {str(e)}")

    def delete_credential(self, cred_id):
        """Delete a credential after confirmation"""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this credential?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_credential(cred_id)
                self.load_data()
                self.statusBar().showMessage("✓ Credential deleted successfully!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete credential: {str(e)}")

    def copy_password(self, encrypted_pass_str):
        """Decrypt and copy password to clipboard"""
        try:
            encrypted_bytes = encrypted_pass_str.encode('utf-8')
            decrypted = CryptoManager.decrypt_data(encrypted_bytes, self.encryption_key)
            ClipboardHelper.copy_with_timeout(decrypted, 10000)
            self.statusBar().showMessage("✓ Password copied! Will clear in 10 seconds.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Decryption failed: {str(e)}")

    def toggle_favorite(self, cred_id):
        """Toggle favorite status"""
        is_favorite = self.db_manager.toggle_favorite(cred_id)
        self.load_data()
        self.statusBar().showMessage(
            "⭐ Added to favorites!" if is_favorite else "Removed from favorites",
            2000
        )

    def filter_by_category(self, row_index):
        """Filter credentials by selected category"""
        if row_index == -1:
            return

        item = self.sidebar.item(row_index)
        if not item:
            return

        cat_text = item.text()

        # Extract category name (remove emoji)
        if "All" in cat_text:
            filtered = self.all_data
        elif "Favorites" in cat_text:
            filtered = self.db_manager.get_favorites()
        else:
            # Extract category name after emoji
            category = cat_text.split(' ', 1)[1] if ' ' in cat_text else cat_text
            filtered = [r for r in self.all_data if r[1] == category]

        self.populate_views(filtered)

    def search_table(self, text):
        """Search credentials by site name or username"""
        text = text.lower()
        if not text:
            self.filter_by_category(self.sidebar.currentRow())
            return

        filtered = [
            r for r in self.all_data
            if text in r[2].lower() or text in r[3].lower()  # site or username
        ]
        self.populate_views(filtered)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_manager.toggle_theme()
        self.apply_theme()
        self.db_manager.set_preference('theme', self.theme_manager.current_theme)

        # Update button icon
        self.theme_toggle_btn.setText("🌙" if self.theme_manager.current_theme == 'light' else "☀️")

    def toggle_view_mode(self):
        """Toggle between table and card view"""
        self.view_mode = 'card' if self.view_mode == 'table' else 'table'
        self.view_stack.setCurrentIndex(0 if self.view_mode == 'table' else 1)
        self.db_manager.set_preference('view_mode', self.view_mode)

        # Update button icon
        self.view_toggle_btn.setText("🗃️" if self.view_mode == 'table' else "📊")
        self.view_toggle_btn.setToolTip(f"Switch to {'Table' if self.view_mode == 'card' else 'Card'} View")

    def apply_theme(self):
        """Apply current theme stylesheet"""
        stylesheet = self.theme_manager.generate_stylesheet()
        self.setStyleSheet(stylesheet)


# Import QLabel (was missing)
from PySide6.QtWidgets import QLabel
