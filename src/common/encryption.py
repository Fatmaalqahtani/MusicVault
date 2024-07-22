from cryptography.fernet import Fernet

def generate_key():
    """Generate and return a new encryption key."""
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    """Encrypt the file at file_path using the provided key."""
    fernet = Fernet(key)
    
    # Read file data
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    # Encrypt data
    encrypted_data = fernet.encrypt(file_data)
    
    # Save encrypted data to a new file
    encrypted_file_path = f"{file_path}.enc"
    with open(encrypted_file_path, 'wb') as file:
        file.write(encrypted_data)
    
    # Return the path of the encrypted file
    return encrypted_file_path
