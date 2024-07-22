import hashlib

def generate_checksum(file_path):
    """Generate and return the SHA-256 checksum of the file at file_path."""
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha256.update(chunk)
    
    return sha256.hexdigest()
