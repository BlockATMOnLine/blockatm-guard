import base64
from typing import List, Dict, Tuple, Union
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto import Random
from Crypto.Hash import SHA256

class AESEngine():

    BLOCK_SIZE = 16  # Bytes
    pad = lambda s: s + (AESEngine.BLOCK_SIZE - len(s) % AESEngine.BLOCK_SIZE) * \
                    chr(AESEngine.BLOCK_SIZE - len(s) % AESEngine.BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    @staticmethod
    def aesencrypt(key, data):
        '''
        AES的ECB模式加密方法
        :param key: 密鑰
        :param data:被加密字符串（明文）
        :return:密文
        '''
        key = key.encode('utf8')
        # 字符串補位
        data = AESEngine.pad(data)
        cipher = AES.new(key, AES.MODE_ECB)
        # 加密後得到的是bytes類型的數據，使用Base64進行編碼,返回byte字符串
        result = cipher.encrypt(data.encode())
        encodestrs = base64.b64encode(result)
        enctext = encodestrs.decode('utf8')
        #print(enctext)
        return enctext

    @staticmethod
    def aesdecrypt(key, data):
        '''
        :param key: 密鑰
        :param data: 加密後的數據（密文）
        :return:明文
        '''
        key = key.encode('utf8')
        data = base64.b64decode(data)
        cipher = AES.new(key, AES.MODE_ECB)

        # 去補位
        text_decrypted = AESEngine.unpad(cipher.decrypt(data))
        text_decrypted = text_decrypted.decode('utf8')
        #print(text_decrypted)
        return text_decrypted
    
class RASEngine():
    @staticmethod
    def create_rsa_key()->Tuple[str]:
        random_gen = Random.new().read
        rsa = RSA.generate(1024, random_gen)

        private_pem = rsa.exportKey()
        #print(f"private_pem = {private_pem}")
        private_key = private_pem.decode()
        #print(f"private_key = {private_key}")
        private_key = private_key.replace('-----BEGIN RSA PRIVATE KEY-----\n', '')
        private_key = private_key.replace('\n-----END RSA PRIVATE KEY-----', '')

        public_pem = rsa.publickey().exportKey()
        public_key = public_pem.decode()
        #print(f"public_pem = {public_pem}")
        #print(f"public_key = {public_key}")
        public_key = public_key.replace('-----BEGIN PUBLIC KEY-----\n', '')
        public_key = public_key.replace('\n-----END PUBLIC KEY-----', '')

        return private_key, public_key
    
    @staticmethod
    def get_ras_key(key):
        key = '-----BEGIN RSA PRIVATE KEY-----\n' + key + "\n-----END RSA PRIVATE KEY-----"
        key = RSA.importKey(key)
        return key
    
    @staticmethod
    def rasencrypt(public_key, data : str)->str:
        #public_key = '-----BEGIN RSA PRIVATE KEY-----\n' + public_key + "\n-----END RSA PRIVATE KEY-----"
        public_key = RASEngine.get_ras_key(public_key)
        cipher = PKCS1_cipher.new(public_key)
        encrypt_text = base64.b64encode(cipher.encrypt(bytes(data.encode("utf8"))))
        return encrypt_text.decode('utf-8')
    
    @staticmethod
    def rasdecrypt(private_key, data : str)->str:
        #private_key = '-----BEGIN RSA PRIVATE KEY-----\n' + private_key + "\n-----END RSA PRIVATE KEY-----"
        private_key = RASEngine.get_ras_key(private_key)
        cipher = PKCS1_cipher.new(private_key)
        back_text = cipher.decrypt(base64.b64decode(data), 0)
        return back_text.decode('utf-8')