import asyncio
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util import Counter
from Crypto.Hash import SHA256
from utils import Color, Style

HOST = 'localhost'
PORT = 8080

async def handle_phone(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    conn_info = { 'device': 'phone' }

    msg = json.dumps(conn_info).encode()

    writer.write(msg)
    await writer.drain()

    rsa_key = RSA.importKey(open('private.pem').read())
    rsa = PKCS1_OAEP.new(rsa_key)

    msg = await reader.read(296)

    aes_hash = msg[:32]
    aes_cipher = msg[32:288]
    nonce = msg[288:296]

    aes_key = rsa.decrypt(aes_cipher)

    if SHA256.new(data=aes_key).digest() != aes_hash: return

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

        if option < 1 or option > 3: continue

        color_option = 0;

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
        data = json.dumps(data).encode()

        data_hash = SHA256.new(data=data).digest()
        data_cipher = aes.encrypt(data)

        msg = data_hash + data_cipher

        writer.write(msg)
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
