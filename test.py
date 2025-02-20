import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
# from db import connectionDriver
load_dotenv()




password = 'my_secure_password'
cipher_pass = b'gAAAAABnsK93ikTMMXKeO5-X8sTPDlEjd5KAuVJMjU58WOHL1PzonHBfk4l1eHt7ulD6Y9DA7pub6ZZELsTuBFXd7HdkgKmIlw=='

class cryptoAgrae():
    __CIPHER__KEY__ = bytes(os.getenv('__CIPHER__KEY__'),'utf-8')
    def __init__(self):
        self.cipher_suite = Fernet(self.__CIPHER__KEY__)
        pass

    def uncrypt(self,value:str):
        return  self.cipher_suite.encrypt(value.encode())

    def decrypt(self,value:str):
        return self.cipher_suite.decrypt(value).decode()

password = '23826405'
# crypt = cryptoAgrae().uncrypt(password)
decrypt = cryptoAgrae().decrypt(cipher_pass)
print(password == decrypt)







