# 🔒 PwKeeper - Password Manager

A secure, modern password manager built with Python and PySide6, featuring a beautiful dark-themed card interface and military-grade encryption.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-Qt-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Introduction

PwKeeper is a cross-platform desktop password manager that prioritizes security and user experience. It uses industry-standard encryption to protect your credentials with a master password, ensuring your sensitive data remains safe even if the database file is compromised.

### Why PwKeeper?

- **🔐 Industry-Standard Encryption**: Your passwords are encrypted using Fernet (AES-128 CBC mode) with PBKDF2 key derivation
- **🎨 Modern UI**: Beautiful dark-themed card interface with responsive design
- **🔍 Smart Search**: Quickly find credentials by site name or username
- **📂 Organized**: Category-based organization with favorites support
- **🎲 Password Generator**: Built-in secure password generator with customizable options
- **📋 Auto-Clear Clipboard**: Passwords automatically clear from clipboard after 10 seconds
- **💾 Local Storage**: Your data never leaves your device

## ✨ Key Features

### Security Features
- **Master Password Protection**: Single master password encrypts all stored credentials
- **PBKDF2 Key Derivation**: 100,000 iterations with unique salt for each user
- **Fernet Encryption**: Symmetric encryption with authentication (AES-128 in CBC mode)
- **Password Strength Checker**: Real-time feedback on password security
- **Secure Password Generator**: Customizable length (8-32 chars) with character type options
- **Auto-Clearing Clipboard**: Copied passwords automatically removed after 10 seconds

### User Interface
- **Card View**: Modern card-based interface for easy credential browsing
- **Responsive Layout**: Dynamically adjusts from 1-4 columns based on window size
- **Dark Theme Only**: Consistent dark mode with purple-blue gradient accents
- **Category Organization**: Organize credentials by General, Social, Work, Finance, or Entertainment
- **Favorites System**: Quick access to frequently used credentials
- **Real-time Search**: Instant filtering by site name or username
- **Clickable URLs**: Direct browser launch from credential cards

### Credential Management
- **Full CRUD Operations**: Create, Read, Update, and Delete credentials
- **Extended Fields**: Store site name, username, password, URL, and notes
- **Category Icons**: Visual identification with emoji icons
- **Favorite Marking**: Star system for important credentials
- **Confirmation Dialogs**: Prevents accidental deletions

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.9+**: Primary programming language
- **PySide6**: Qt for Python - GUI framework
- **SQLite3**: Built-in database for credential storage
- **Cryptography**: Industry-standard encryption library (Fernet)

### Dependencies
```
PySide6       # Qt-based GUI framework
cryptography  # Encryption and key derivation
pytest        # Testing framework
pyinstaller   # Standalone executable builder
```

### Encryption Stack
- **Algorithm**: Fernet (symmetric encryption)
  - Cipher: AES-128-CBC
  - MAC: HMAC-SHA256
  - Encoding: Base64 URL-safe
- **Key Derivation**: PBKDF2-HMAC-SHA256
  - Iterations: 100,000
  - Salt: 16 bytes (unique per installation)
  - Key Length: 32 bytes

## 📁 Project Structure

```
PwKeeper/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── db_manager.py          # SQLite database operations
│   │   └── crypto_manager.py      # Encryption/decryption logic
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py         # Main application window
│   │   ├── login_dialog.py        # Master password authentication
│   │   ├── credential_dialog.py   # Add/Edit credential form
│   │   ├── password_generator_dialog.py  # Password generation tool
│   │   ├── card_view.py           # Card-based credential display
│   │   └── theme_manager.py       # Dark theme styling
│   └── utils/
│       ├── __init__.py
│       ├── password_utils.py      # Password strength & generation
│       └── clipboard.py           # Secure clipboard operations
├── tests/
│   └── test_core.py               # Unit tests
├── requirements.txt               # Python dependencies
├── build.sh                       # Build script for macOS app
└── README.md                      # This file
```

## 🚀 Installation & Usage

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jason960028/PWsaver.git
   cd PwKeeper
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Development Mode:**
```bash
python src/main.py
```

**First Launch:**
- You'll be prompted to create a master password
- Choose a strong password (you'll see strength feedback)
- This password cannot be recovered if lost!

**Subsequent Launches:**
- Enter your master password to unlock the vault
- Wrong password will be rejected with a warning

### Building Standalone Executable

**macOS:**
```bash
./build.sh
# Output: dist/PwKeeper.app
```

**Note:** Currently tested on macOS. Windows/Linux builds may require additional configuration.

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

### Test Coverage
- Core encryption/decryption
- Key derivation functions
- Password strength checking
- Password generation
- Database operations

## 🔒 Security Design Details

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           User Interface Layer                  │
│  (LoginDialog, MainWindow, CredentialDialog)    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         Application Logic Layer                 │
│  (CryptoManager, DBManager, PasswordUtils)      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│           Data Storage Layer                    │
│    (SQLite Database - password_keeper.db)       │
│    [Encrypted Credentials] [Settings] [Prefs]   │
└─────────────────────────────────────────────────┘
```

### Encryption Workflow

**Setup Phase (First Run):**
1. User creates master password
2. Generate random 16-byte salt
3. Derive encryption key using PBKDF2 (100k iterations)
4. Create verifier token by encrypting "VERIFIED"
5. Store salt (hex) and verifier (base64) in database

**Login Phase:**
1. Retrieve salt from database
2. User enters master password
3. Derive key using PBKDF2 with stored salt
4. Attempt to decrypt verifier token
5. If decryption succeeds and yields "VERIFIED", grant access

**Credential Storage:**
1. User enters credential data
2. Password encrypted with derived key using Fernet
3. Store encrypted password as base64 string
4. Store other fields in plaintext (site, username, url, notes)

**Credential Retrieval:**
1. Fetch encrypted password from database
2. Decrypt using current session's encryption key
3. Display or copy to clipboard
4. If clipboard, auto-clear after 10 seconds

### Security Guarantees

✅ **Master Password Not Stored**: Only the verifier token is stored
✅ **Unique Salt Per Installation**: Prevents rainbow table attacks
✅ **Key Stretching**: 100,000 PBKDF2 iterations slow down brute-force attacks
✅ **Authenticated Encryption**: Fernet includes HMAC for integrity verification
✅ **Auto-Clear Clipboard**: Passwords automatically removed after 10 seconds
✅ **No Network Access**: All data stored locally

### Threat Model

**Protected Against:**
- Database file theft (credentials remain encrypted)
- Brute-force attacks on weak master passwords (key stretching)
- Password interception in memory (auto-clear clipboard)
- Rainbow table attacks (unique salt)

**Not Protected Against:**
- Keyloggers capturing master password
- Memory dumps while application is running
- Master password compromise
- Physical access with master password
- OS-level attacks (malware, root access)

### Best Practices for Users

1. **Choose a Strong Master Password**
   - Minimum 12 characters
   - Mix uppercase, lowercase, numbers, symbols
   - Avoid dictionary words and personal info
   - Use password strength meter as guide

2. **Protect Your Master Password**
   - Never share it
   - Don't write it down
   - Use a passphrase instead of a password
   - If forgotten, data cannot be recovered

3. **Regular Backups**
   - Backup `password_keeper.db` regularly
   - Store backups securely (encrypted external drive)
   - Test backup restoration

4. **System Security**
   - Use full-disk encryption
   - Keep OS and antivirus updated
   - Avoid using on shared/public computers
   - Lock screen when away

## 📄 License

MIT License

Copyright (c) 2025 Jason Park

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

Jason Park - [@Jason960028](https://github.com/Jason960028)

Project Link: [https://github.com/Jason960028/PWsaver](https://github.com/Jason960028/PWsaver)

---

**⚠️ Disclaimer**: This software is provided as-is for educational and personal use. While it implements industry-standard encryption, no software can guarantee 100% security. Use at your own risk and always maintain backups of important data.
