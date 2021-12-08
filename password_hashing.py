import hashlib
import os

def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt+key

def check_hash(storage, password):
    salt_from_storage = storage[:32]
    hash_from_storage = storage[32:]
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_from_storage, 100000)
    if key == hash_from_storage:
        return True
    else:
        return False

def check_password(workspace, password):
    file = open(os.path.join('workspace', workspace, 'password.hash'), 'rb')
    result = check_hash(file.read(), password)
    file.close()
    return result