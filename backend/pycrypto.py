import base64
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


# 生成密钥对
def generateKeypair():
    # 伪随机数,创建rsa算法实例
    random_generator = Random.new().read
    rsa = RSA.generate(1024, random_generator)
    # 生成秘钥对
    private_pem = rsa.exportKey()
    public_pem = rsa.publickey().exportKey()
    return {
        "public_pem": public_pem,
        "private_pem": private_pem,
        "random_generator": random_generator
    }


# 加密数据
def encrypt(publicKey, msg):
    # 用公钥加密，被加密的数据后面.encode("utf8")不能省略
    message = msg.encode("utf8")
    # 导入公钥加密并对数据加密（后使用）
    rsakey = RSA.importKey(publicKey)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(message))
    print("加密后：", cipher_text)
    return cipher_text


# 解密数据
def decrypt(privateKey, msg, random_generator):
    # 用私钥解密
    rsakey = RSA.importKey(privateKey)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    # 使用base64解密，(在前端js加密时自动是base64加密)
    text = cipher.decrypt(base64.b64decode(msg), random_generator)
    return text
