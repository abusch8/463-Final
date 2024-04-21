import asyncio
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util import Counter

HOST = 'localhost'
PORT = 8080

async def start_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)

    cipher = await reader.read(256)

    rsa_key = RSA.importKey(open('private.pem').read())
    rsa = PKCS1_OAEP.new(rsa_key)
    aes_key = rsa.decrypt(cipher)

    nonce = await reader.read(8)

    ctr = Counter.new(64, prefix=nonce, initial_value=1)
    aes = AES.new(aes_key, AES.MODE_CTR, counter=ctr)

    while True:
        msg = input('>> ')

        cipher = aes.encrypt(msg.encode())
        writer.write(cipher)

if __name__ == '__main__':
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print('\nDisconnecting...')
        exit()
