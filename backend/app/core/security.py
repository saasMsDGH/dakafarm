from pwdlib import PasswordHash

hashed_password = PasswordHash.recommended()

class Hash():

    @staticmethod
    def hash(password):
        return hashed_password.hash(password)

    @staticmethod
    def verify_password(plain_password,hashed_pasword):
        return hashed_password.verify(plain_password,hashed_pasword)