import os
import pytest
import base64
from src.core.crypto_manager import CryptoManager
from src.core.db_manager import DBManager

# --- Crypto Tests ---
def test_salt_generation():
    salt = CryptoManager.generate_salt()
    assert len(salt) == 16
    assert isinstance(salt, bytes)

def test_key_derivation():
    password = "my_secret_password"
    salt = CryptoManager.generate_salt()
    key = CryptoManager.derive_key(password, salt)
    
    # Fernet key must be 32 bytes base64 encoded
    assert len(base64.urlsafe_b64decode(key)) == 32

    # Deterministic check
    key2 = CryptoManager.derive_key(password, salt)
    assert key == key2

def test_encrypt_decrypt():
    password = "master_password"
    salt = CryptoManager.generate_salt()
    key = CryptoManager.derive_key(password, salt)
    
    secret_data = "GoogleDeepMind"
    encrypted = CryptoManager.encrypt_data(secret_data, key)
    
    assert encrypted != secret_data
    
    decrypted = CryptoManager.decrypt_data(encrypted, key)
    assert decrypted == secret_data

# --- DB Tests ---
@pytest.fixture
def db():
    # Setup
    test_db_path = "test_pwkeeper.db"
    manager = DBManager(test_db_path)
    yield manager
    # Teardown
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_db_settings(db):
    db.set_setting("master_salt", "somesaltvalue")
    val = db.get_setting("master_salt")
    assert val == "somesaltvalue"

def test_credential_crud(db):
    # Create
    uid = db.add_credential("Social", "Facebook", "jason@gmail.com", "encrypted_blob")
    assert uid is not None
    
    # Read
    creds = db.get_all_credentials()
    assert len(creds) == 1
    assert creds[0][1] == "Social" # category
    assert creds[0][2] == "Facebook" # site_name
    
    # Update
    db.update_credential(uid, "Work", "LinkedIn", "jason@linkedin.com", "new_blob")
    updated = db.get_credential_by_id(uid)
    assert updated[1] == "Work"
    assert updated[2] == "LinkedIn"
    
    # Delete
    db.delete_credential(uid)
    assert len(db.get_all_credentials()) == 0
