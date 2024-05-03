import asyncio
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util import Counter

HOST = 'localhost'
PORT = 8080

class Color():
    RED     = chr(27) + '[31m'
    YELLOW  = chr(27) + '[33m'
    BLUE    = chr(27) + '[34m'

class Style():
    RESET   = chr(27) + '[0m'
    CLEAR   = chr(27) + '[2J'

async def start_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)

    conn_info = { 'device': 'phone' }

    writer.write(json.dumps(conn_info).encode())

    cipher = await reader.read(256)

    rsa_key = RSA.importKey(open('private.pem').read())
    rsa = PKCS1_OAEP.new(rsa_key)
    aes_key = rsa.decrypt(cipher)

    nonce = await reader.read(8)

    ctr = Counter.new(64, prefix=nonce, initial_value=1)
    aes = AES.new(aes_key, AES.MODE_CTR, counter=ctr)

    while True:
        print(Style.CLEAR)

        print('1) Toggle light')
        print('2) Change color')
        print('3) Disconnect')

        option = int(input('>> '))
        color_option = 0;

        if option < 1 or option > 3: continue

        if option == 2:
            print(Style.CLEAR)

            print(f'1) {Color.RED}Red{Style.RESET}')
            print(f'2) {Color.YELLOW}Yellow{Style.RESET}')
            print(f'3) {Color.BLUE}Blue{Style.RESET}')
            print('4) Default')

            color_option = int(input('>> '))

            if color_option < 1 or color_option > 4: continue

        data = {
            'device':   'phone',
            'option':   option,
            'color':    color_option,
        }

        msg = json.dumps(data)
        cipher = aes.encrypt(msg.encode())
        writer.write(cipher)

def main():
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print('\nDisconnecting...')
        exit()

if __name__ == '__main__':
    main()
