from Crypto.Cipher import AES
import base64


BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def aesencrypt(key, data):
    '''
    AES的ECB模式加密方法
    :param key: 密鑰
    :param data:被加密字符串（明文）
    :return:密文
    '''
    key = key.encode('utf8')
    # 字符串補位
    data = pad(data)
    cipher = AES.new(key, AES.MODE_ECB)
    # 加密後得到的是bytes類型的數據，使用Base64進行編碼,返回byte字符串
    result = cipher.encrypt(data.encode())
    encodestrs = base64.b64encode(result)
    enctext = encodestrs.decode('utf8')
    #print(enctext)
    return enctext

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
    text_decrypted = unpad(cipher.decrypt(data))
    text_decrypted = text_decrypted.decode('utf8')
    #print(text_decrypted)
    return text_decrypted


# if __name__ == '__main__':
#     key = 'b2b@github@2023.'
#     import requests
#     #data = 'fw2pG6kPmLgJg6k1nQFBWThVhIuiOW6Y9OK0V01cakwF7aT7bqYdvHG8tfSuqZFev6SfqVNgU9srALWJci6fgKi9gicsv/rqV/+UnmKmgU9vu+5fOoORCAPIN7atgp1+bdokHh9vPa04rtdTvZ49sQoA/GKqALe1PebErNAxO1P6+W6EgKrNem696E3cRXzBLSdfFI5Usv0qeAxHmR+HxeVADXRLXzFWXl/SK062XP9BYKdH46K7axo94omdh74wJgJUElpohBYi+1Mc6nPA0YmM1SsD4Z4/7NkicocXgALRIH4sYKOOB+pT6ADGbltu92cJGvDPZ9bIoZn+UhDZ1KOpzmAm9OU3TKIP3CA8wSQux6bLD6Wbs3cKWCDl5wza1rgoeB0YCVqSiL7oo/EscQ=='
#     url = 'https://github.com/shlangelhu/shl-desktop-agent/raw/main/configurations/19.yaml'
#     res = requests.get(url, timeout=5)
#     #ecdata = aesEncrypt(key, data)
#     de_data =aesDecrypt(key, res.text)

#     import yaml
#     print(yaml.safe_load(de_data))
    

