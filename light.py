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
    DEFAULT = chr(27) + '[39m'

    def enum(i):
        return {
            1: Color.RED,
            2: Color.YELLOW,
            3: Color.BLUE,
            4: Color.DEFAULT,
        }[i]

class Style():
    RESET   = chr(27) + '[0m'
    BOLD    = chr(27) + '[1m'
    CLEAR   = chr(27) + '[2J'

class Bulb():
    def __init__(self):
        self.state = False
        self.color = Color.DEFAULT

    def print(self):
        print(f"""{Style.CLEAR}{Style.BOLD}{self.color}{
            """
         :
     '.  _  .'
    -=  (~)  =-
     .'  #  '.

            """
            if self.state else
            """

         _
        (~)
         #

            """
           }{Style.RESET}""")

async def start_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)

    conn_info = { 'device': 'light' }

    writer.write(json.dumps(conn_info).encode())

    nonce = await reader.read(8)
    ctr = Counter.new(64, prefix=nonce, initial_value=1)

    aes = AES.new(open('aes-128.key', 'rb').read(), AES.MODE_CTR, counter=ctr)

    bulb = Bulb()

    while True:
        bulb.print()

        cipher = await reader.read(1024)

        if not cipher: break

        msg = aes.decrypt(cipher).decode()

        data = json.loads(msg)

        if data['option'] == 1:
            bulb.state = not bulb.state
        elif data['option'] == 2:
            bulb.color = Color.enum(data['color'])

def main():
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print('\nDisconnecting...')
        exit()

if __name__ == '__main__':
    main()
