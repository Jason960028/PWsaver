# Theme Manager for PwKeeper
# Handles light/dark theme switching and stylesheet generation

LIGHT_THEME = {
    # Backgrounds
    'bg_primary': '#ffffff',
    'bg_secondary': '#f7f7f9',
    'bg_sidebar': '#f0f2f5',
    'bg_elevated': '#ffffff',

    # Gradients (Purple/Blue)
    'gradient_start': '#667eea',
    'gradient_end': '#5b9ff5',

    # Accent colors
    'accent_primary': '#7c3aed',
    'accent_secondary': '#2563eb',
    'accent_success': '#10b981',
    'accent_warning': '#f59e0b',
    'accent_danger': '#ef4444',

    # Text
    'text_primary': '#1f2937',
    'text_secondary': '#6b7280',
    'text_tertiary': '#9ca3af',
    'text_inverse': '#ffffff',

    # Borders
    'border_light': '#e5e7eb',
    'border_medium': '#d1d5db',
    'border_dark': '#9ca3af',

    # Special
    'hover_bg': 'rgba(124, 58, 237, 0.05)',
    'selected_bg': 'rgba(124, 58, 237, 0.1)',
}

DARK_THEME = {
    # Backgrounds
    'bg_primary': '#1e1e2e',
    'bg_secondary': '#181825',
    'bg_sidebar': '#11111b',
    'bg_elevated': '#313244',

    # Gradients (Purple/Blue - brighter for dark)
    'gradient_start': '#8b5cf6',
    'gradient_end': '#3b82f6',

    # Accent colors
    'accent_primary': '#a78bfa',
    'accent_secondary': '#60a5fa',
    'accent_success': '#34d399',
    'accent_warning': '#fbbf24',
    'accent_danger': '#f87171',

    # Text
    'text_primary': '#cdd6f4',
    'text_secondary': '#bac2de',
    'text_tertiary': '#6c7086',
    'text_inverse': '#1e1e2e',

    # Borders
    'border_light': '#313244',
    'border_medium': '#45475a',
    'border_dark': '#585b70',

    # Special
    'hover_bg': 'rgba(167, 139, 250, 0.1)',
    'selected_bg': 'rgba(167, 139, 250, 0.15)',
}

# Icon mappings
ICONS = {
    # Categories
    'all': '🌐',
    'general': '📋',
    'social': '👥',
    'work': '💼',
    'finance': '💰',
    'entertainment': '🎮',

    # Actions
    'add': '➕',
    'search': '🔍',
    'copy': '📋',
    'edit': '✏️',
    'delete': '🗑️',
    'star': '⭐',
    'star_outline': '☆',
    'eye': '👁',
    'eye_off': '🙈',
    'refresh': '🔄',
    'settings': '⚙️',
    'moon': '🌙',
    'sun': '☀️',
    'lock': '🔒',
    'key': '🔑',
    'check': '✓',
    'close': '✕',
    'generate': '🎲',
    'table_view': '📊',
    'card_view': '🗃️',
}


class ThemeManager:
    def __init__(self, initial_theme='light'):
        self.current_theme = initial_theme
        self.themes = {
            'light': LIGHT_THEME,
            'dark': DARK_THEME
        }

    def get_color(self, key):
        """Get a color value from the current theme"""
        return self.themes[self.current_theme].get(key, '#000000')

    def toggle_theme(self):
        """Switch between light and dark themes"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        return self.current_theme

    def set_theme(self, theme_name):
        """Set theme directly by name"""
        if theme_name in self.themes:
            self.current_theme = theme_name

    def is_dark(self):
        """Check if current theme is dark"""
        return self.current_theme == 'dark'

    def generate_stylesheet(self):
        """Generate complete QSS stylesheet based on current theme"""
        theme = self.themes[self.current_theme]

        qss = f"""
/* ===== GLOBAL STYLES ===== */
QWidget {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
    color: {theme['text_primary']};
    background-color: {theme['bg_primary']};
}}

QMainWindow {{
    background-color: {theme['bg_primary']};
}}

/* ===== SIDEBAR ===== */
QListWidget {{
    background-color: {theme['bg_sidebar']};
    border: none;
    border-right: 1px solid {theme['border_light']};
    outline: none;
    padding: 8px;
}}

QListWidget::item {{
    padding: 12px 16px;
    margin: 4px 0px;
    border-radius: 8px;
    color: {theme['text_primary']};
}}

QListWidget::item:hover {{
    background-color: {theme['hover_bg']};
}}

QListWidget::item:selected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {theme['gradient_start']}, stop:1 {theme['gradient_end']});
    color: {theme['text_inverse']};
    font-weight: 600;
}}

/* ===== TABLE ===== */
QTableWidget {{
    border: none;
    gridline-color: {theme['border_light']};
    selection-background-color: {theme['selected_bg']};
    selection-color: {theme['text_primary']};
    background-color: {theme['bg_primary']};
    alternate-background-color: {theme['bg_secondary']};
}}

QTableWidget::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:hover {{
    background-color: {theme['hover_bg']};
}}

QHeaderView::section {{
    background-color: {theme['bg_secondary']};
    padding: 12px 8px;
    border: none;
    border-bottom: 2px solid {theme['accent_primary']};
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    color: {theme['text_secondary']};
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: {theme['bg_elevated']};
    border: 1px solid {theme['border_medium']};
    border-radius: 8px;
    padding: 8px 16px;
    min-width: 60px;
    color: {theme['text_primary']};
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {theme['bg_secondary']};
    border-color: {theme['border_dark']};
}}

QPushButton:pressed {{
    background-color: {theme['border_light']};
}}

/* Primary Button (Gradient) */
QPushButton#primaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {theme['gradient_start']}, stop:1 {theme['gradient_end']});
    color: {theme['text_inverse']};
    border: none;
    font-weight: 600;
}}

QPushButton#primaryBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {theme['accent_primary']}, stop:1 {theme['accent_secondary']});
}}

QPushButton#primaryBtn:pressed {{
    background: {theme['accent_primary']};
}}

/* Success Button */
QPushButton#successBtn {{
    background-color: {theme['accent_success']};
    color: white;
    border: none;
    font-weight: 600;
}}

QPushButton#successBtn:hover {{
    background-color: {theme['accent_success']};
    opacity: 0.9;
}}

/* Danger Button */
QPushButton#dangerBtn {{
    background-color: {theme['accent_danger']};
    color: white;
    border: none;
    font-weight: 600;
}}

QPushButton#dangerBtn:hover {{
    background-color: {theme['accent_danger']};
    opacity: 0.9;
}}

/* Secondary Button (Outlined) */
QPushButton#secondaryBtn {{
    background-color: transparent;
    border: 2px solid {theme['accent_primary']};
    color: {theme['accent_primary']};
}}

QPushButton#secondaryBtn:hover {{
    background-color: {theme['hover_bg']};
}}

/* Icon Button (Small, Square) */
QPushButton#iconBtn {{
    padding: 8px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    border-radius: 6px;
}}

/* ===== INPUT FIELDS ===== */
QLineEdit {{
    border: 1px solid {theme['border_medium']};
    border-radius: 8px;
    padding: 8px 12px;
    background-color: {theme['bg_elevated']};
    color: {theme['text_primary']};
    selection-background-color: {theme['accent_primary']};
}}

QLineEdit:focus {{
    border: 2px solid {theme['accent_primary']};
    padding: 7px 11px;
}}

QLineEdit::placeholder {{
    color: {theme['text_tertiary']};
}}

/* ===== TEXT EDIT ===== */
QTextEdit {{
    border: 1px solid {theme['border_medium']};
    border-radius: 8px;
    padding: 8px 12px;
    background-color: {theme['bg_elevated']};
    color: {theme['text_primary']};
}}

QTextEdit:focus {{
    border: 2px solid {theme['accent_primary']};
}}

/* ===== COMBOBOX ===== */
QComboBox {{
    border: 1px solid {theme['border_medium']};
    border-radius: 8px;
    padding: 8px 12px;
    background-color: {theme['bg_elevated']};
    color: {theme['text_primary']};
}}

QComboBox:hover {{
    border-color: {theme['border_dark']};
}}

QComboBox:focus {{
    border: 2px solid {theme['accent_primary']};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid {theme['border_medium']};
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}}

QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {theme['bg_elevated']};
    border: 1px solid {theme['border_medium']};
    border-radius: 8px;
    selection-background-color: {theme['accent_primary']};
    selection-color: {theme['text_inverse']};
    padding: 4px;
}}

/* ===== PROGRESS BAR ===== */
QProgressBar {{
    border: 1px solid {theme['border_light']};
    border-radius: 6px;
    text-align: center;
    background-color: {theme['bg_secondary']};
    height: 8px;
}}

QProgressBar::chunk {{
    border-radius: 5px;
}}

/* Strength meter colors - will be set dynamically */
QProgressBar#strengthWeak::chunk {{
    background-color: {theme['accent_danger']};
}}

QProgressBar#strengthMedium::chunk {{
    background-color: {theme['accent_warning']};
}}

QProgressBar#strengthStrong::chunk {{
    background-color: {theme['accent_success']};
}}

/* ===== DIALOG ===== */
QDialog {{
    background-color: {theme['bg_primary']};
}}

QDialogButtonBox {{
    dialogbuttonbox-buttons-have-icons: 0;
}}

/* ===== LABELS ===== */
QLabel {{
    color: {theme['text_primary']};
    background: transparent;
}}

QLabel#titleLabel {{
    font-size: 18px;
    font-weight: 600;
    color: {theme['text_primary']};
}}

QLabel#subtitleLabel {{
    font-size: 15px;
    font-weight: 500;
    color: {theme['text_secondary']};
}}

QLabel#captionLabel {{
    font-size: 11px;
    color: {theme['text_tertiary']};
}}

/* ===== STATUSBAR ===== */
QStatusBar {{
    background-color: {theme['bg_secondary']};
    color: {theme['text_secondary']};
    border-top: 1px solid {theme['border_light']};
}}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {{
    border: none;
    background: {theme['bg_secondary']};
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {theme['border_dark']};
    min-height: 20px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {theme['accent_primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {theme['bg_secondary']};
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {theme['border_dark']};
    min-width: 20px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {theme['accent_primary']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ===== CHECKBOX ===== */
QCheckBox {{
    spacing: 8px;
    color: {theme['text_primary']};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {theme['border_dark']};
    background-color: {theme['bg_elevated']};
}}

QCheckBox::indicator:hover {{
    border-color: {theme['accent_primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {theme['accent_primary']};
    border-color: {theme['accent_primary']};
}}

/* ===== SLIDER ===== */
QSlider::groove:horizontal {{
    border: none;
    height: 6px;
    background: {theme['bg_secondary']};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {theme['accent_primary']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {theme['gradient_start']};
}}

/* ===== TOOLTIP ===== */
QToolTip {{
    background-color: {theme['bg_elevated']};
    color: {theme['text_primary']};
    border: 1px solid {theme['border_medium']};
    border-radius: 6px;
    padding: 6px 10px;
}}

/* ===== MESSAGE BOX ===== */
QMessageBox {{
    background-color: {theme['bg_primary']};
}}

QMessageBox QLabel {{
    color: {theme['text_primary']};
}}

/* ===== HEADER BAR ===== */
QWidget#headerBar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {theme['gradient_start']}, stop:1 {theme['gradient_end']});
    border-bottom: 2px solid {theme['accent_primary']};
}}

QWidget#headerBar QLabel {{
    color: {theme['text_inverse']};
}}

/* ===== CARD VIEW ===== */
QFrame#credentialCard {{
    background-color: {theme['bg_elevated']};
    border: 1px solid {theme['border_light']};
    border-radius: 12px;
    padding: 4px;
}}

QFrame#credentialCard:hover {{
    border: 2px solid {theme['accent_primary']};
    background-color: {theme['bg_elevated']};
}}

QLabel#categoryBadge {{
    background-color: {theme['bg_secondary']};
    color: {theme['text_secondary']};
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
}}

QLabel#cardTitle {{
    font-size: 18px;
    font-weight: 700;
    color: {theme['text_primary']};
}}

QFrame#cardDivider {{
    color: {theme['border_light']};
}}

QLabel#cardUsername {{
    font-size: 11px;
    color: {theme['text_secondary']};
}}

QLabel#cardUrl {{
    font-size: 10px;
    color: {theme['accent_primary']};
    text-decoration: underline;
}}

QLabel#cardUrl:hover {{
    color: {theme['gradient_start']};
}}

QLabel#cardNotes {{
    font-size: 9px;
    color: {theme['text_tertiary']};
    font-style: italic;
}}

QPushButton#cardActionBtn {{
    background-color: {theme['bg_secondary']};
    border: 1px solid {theme['border_light']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {theme['text_primary']};
    font-weight: 500;
    font-size: 12px;
}}

QPushButton#cardActionBtn:hover {{
    background-color: {theme['hover_bg']};
    border-color: {theme['accent_primary']};
}}

/* ===== EMPTY STATE ===== */
QLabel#emptyStateTitle {{
    font-size: 18px;
    font-weight: 700;
    color: {theme['text_primary']};
}}

QLabel#emptyStateHint {{
    font-size: 12px;
    color: {theme['text_tertiary']};
}}
"""
        return qss

    def get_icon(self, name):
        """Get an icon character by name"""
        return ICONS.get(name, '')
