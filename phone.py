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
    GREEN   = chr(27) + '[32m'
    YELLOW  = chr(27) + '[33m'
    BLUE    = chr(27) + '[34m'
    PURPLE  = chr(27) + '[35m'
    CYAN    = chr(27) + '[36m'
    DEFAULT = chr(27) + '[39m'

class Style():
    RESET   = chr(27) + '[0m'
    CLEAR   = chr(27) + '[2J' + chr(27) + '[H'

async def handle_phone(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    conn_info = { 'device': 'phone' }

    writer.write(json.dumps(conn_info).encode())
    await writer.drain()

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

        try:
            option = int(input('>> '))
        except ValueError:
            continue

        color_option = 0;

        if option < 1 or option > 3: continue

        if option == 2:
            print(Style.CLEAR)

            print(f'1) {Color.RED}Red{Style.RESET}')
            print(f'2) {Color.GREEN}Green{Style.RESET}')
            print(f'3) {Color.YELLOW}Yellow{Style.RESET}')
            print(f'4) {Color.BLUE}Blue{Style.RESET}')
            print(f'5) {Color.PURPLE}Purple{Style.RESET}')
            print(f'6) {Color.CYAN}Cyan{Style.RESET}')
            print(f'7) {Color.DEFAULT}Default{Style.RESET}')

            try:
                color_option = int(input('>> '))
            except ValueError:
                continue

            if color_option < 1 or color_option > 7: continue

        data = { **conn_info, 'option': option, 'color': color_option }

        writer.write(aes.encrypt(json.dumps(data).encode()))
        await writer.drain()

async def start_client():
    writer = None
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        await handle_phone(reader, writer)
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
    except (KeyboardInterrupt, BrokenPipeError):
        return

if __name__ == '__main__':
    main()
