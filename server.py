import asyncio
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter
from Crypto.Hash import SHA256

HOST = 'localhost'
PORT = 8080

lights = []

async def handle_phone(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    peer_addr = writer.get_extra_info('peername')

    rsa_key = RSA.importKey(open('public.pem').read())
    rsa = PKCS1_OAEP.new(rsa_key)

    aes_key = get_random_bytes(16)

    aes_hash = SHA256.new(data=aes_key).digest()
    aes_cipher = rsa.encrypt(aes_key)
    nonce = get_random_bytes(8)

    msg = aes_hash + aes_cipher + nonce

    writer.write(msg)
    await writer.drain()

    ctr = Counter.new(64, prefix=nonce, initial_value=1)
    aes = AES.new(aes_key, AES.MODE_CTR, counter=ctr)

    while True:
        msg = await reader.read(1024)

        if not msg: return

        data_hash = msg[:32]
        data_cipher = msg[32:]

        data = aes.decrypt(data_cipher)

        if SHA256.new(data=data).digest() != data_hash: return

        for light in lights:
            data_cipher = light['aes'].encrypt(data)

            msg = data_hash + data_cipher

            light['writer'].write(msg)
            await light['writer'].drain()

        print(f'[{peer_addr[0]}:{peer_addr[1]}]: {data.decode()}')

async def handle_light(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    nonce = get_random_bytes(8)

    writer.write(nonce)
    await writer.drain()

    ctr = Counter.new(64, prefix=nonce, initial_value=1)
    aes = AES.new(open('aes-128.key', 'rb').read(), AES.MODE_CTR, counter=ctr)

    data = { 'reader': reader, 'writer': writer, 'aes': aes }

    lights.append(data)
    if not await reader.read(): lights.remove(data)

async def handle_conn(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    peer_addr = writer.get_extra_info('peername')
    conn_info = json.loads((await reader.read(1024)).decode())

    device = conn_info['device']

    print(f'Connected by {device} @ {peer_addr[0]}:{peer_addr[1]}')

    if device == 'phone':
        await handle_phone(reader, writer)
    elif device == 'light':
        await handle_light(reader, writer)
    else:
        return

    print(f'Disconnect by {device} @ {peer_addr[0]}:{peer_addr[1]}')

async def start_server():
    server = None
    try:
        server = await asyncio.start_server(handle_conn, HOST, PORT)
        print(f'Socket server started @ {HOST}:{PORT}')
        async with server: await server.serve_forever()
    except ConnectionError as e:
        print(f'{e.__class__.__name__} @ {HOST}:{PORT}')
    finally:
        if server:
            print('Shutting down...')
            server.close()
            await server.wait_closed()

def main():
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    main()
