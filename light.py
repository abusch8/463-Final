import asyncio
import json
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Hash import SHA256

HOST = 'localhost'
PORT = 8080

class Color():
    RED     = chr(27) + '[31m'
    GREEN   = chr(27) + '[32m'
    YELLOW  = chr(27) + '[33m'
    BLUE    = chr(27) + '[34m'
    PURPLE  = chr(27) + '[35m'
    CYAN    = chr(27) + '[36m'
    DEFAULT = chr(27) + '[39m'

    def enum(i: int) -> str:
        return {
            1: Color.RED,
            2: Color.GREEN,
            3: Color.YELLOW,
            4: Color.BLUE,
            5: Color.PURPLE,
            6: Color.CYAN,
            7: Color.DEFAULT,
        }[i]

class Style():
    RESET   = chr(27) + '[0m'
    BOLD    = chr(27) + '[1m'
    CLEAR   = chr(27) + '[2J' + chr(27) + '[H'

class Bulb():
    def __init__(self):
        self.state = 0
        self.color = Color.DEFAULT

    def toggle_state(self):
        self.state = int(not self.state)

    def set_color(self, i: int):
        self.color = Color.enum(i)

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

async def handle_light(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    conn_info = { 'device': 'light' }

    msg = json.dumps(conn_info).encode()

    writer.write(msg)
    await writer.drain()

    nonce = await reader.read(8)

    ctr = Counter.new(64, prefix=nonce, initial_value=1)
    aes = AES.new(open('aes-128.key', 'rb').read(), AES.MODE_CTR, counter=ctr)

    bulb = Bulb()

    while True:
        bulb.print()

        msg = await reader.read(1024)

        if not msg: raise ConnectionResetError

        data_hash = msg[:32]
        data_cipher = msg[32:]

        data = aes.decrypt(data_cipher)

        if SHA256.new(data=data).digest() != data_hash: return

        data = json.loads(data.decode())
        option, color = data['option'], data['color']

        if option == 1:
            bulb.toggle_state()
        elif option == 2:
            bulb.set_color(color)
        elif option == 3:
            raise ConnectionAbortedError

async def start_client():
    writer = None
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        await handle_light(reader, writer)
    except ConnectionError as e:
        print(f'{e.__class__.__name__} @ {HOST}:{PORT}')
    finally:
        if writer:
            print('Disconnecting...')
            writer.close()
            await writer.wait_closed()

def main():
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    main()
