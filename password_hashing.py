import hashlib
import os

# This function is for making a new password hash
def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt+key

# This funcion checks a password against a hash + salt
def check_hash(storage, password):
    # The salt and hash are stored together in a single file, so we need to seperate them here
    salt_from_storage = storage[:32]
    hash_from_storage = storage[32:]
    # Since hashes aren't reversible you check them by hasing the password to be checked by running it through the same
    # hashing algorithm with the salt we used to make the original password hash.
    # This salt is stored along with the password hash specifically for checking passwords like this
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_from_storage, 100000)
    if key == hash_from_storage:
        return True
    else:
        return False

def check_password(workspace, password):
    # The password hashes are stored in a file rather than in a database.
    # It was determined this would be easier than using a database since all we are really storing besides passwords
    # information is a set of files and directories
    file = open(os.path.join('workspace', workspace, 'password.hash'), 'rb')
    result = check_hash(file.read(), password)
    file.close()
    return result