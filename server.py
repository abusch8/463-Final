import asyncio
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter

HOST = 'localhost'
PORT = 8080

lights = []

async def handle_phone(reader, writer):
    peer_addr = writer.get_extra_info('peername')

    aes_key = get_random_bytes(16)
    rsa_key = RSA.importKey(open('public.pem').read())
    rsa = PKCS1_OAEP.new(rsa_key)

    cipher = rsa.encrypt(aes_key)
    writer.write(cipher)

    nonce = get_random_bytes(8)
    writer.write(nonce)

    ctr = Counter.new(64, prefix=nonce, initial_value=1)
    aes = AES.new(aes_key, AES.MODE_CTR, counter=ctr)

    while True:
        cipher = await reader.read(1024)

        if not cipher:
            print(f'Disconnect by {peer_addr}')
            break

        msg = aes.decrypt(cipher).decode()

        for light in lights:
            cipher = light['aes'].encrypt(msg.encode())
            light['writer'].write(cipher)

        print(f'{peer_addr}: {msg}')

async def handle_light(reader, writer):

    nonce = get_random_bytes(8)
    writer.write(nonce)

    ctr = Counter.new(64, prefix=nonce, initial_value=1)
    aes = AES.new(open('aes-128.key', 'rb').read(), AES.MODE_CTR, counter=ctr)

    lights.append({ 'reader': reader, 'writer': writer, 'aes': aes })

async def handle_conn(reader, writer):
    peer_addr = writer.get_extra_info('peername')

    header = await reader.read(1024)

    conn_info = json.loads(header.decode())

    print(f'Connected by {conn_info['device']} @ {peer_addr}')

    if conn_info['device'] == 'phone':
        await handle_phone(reader, writer)
    elif conn_info['device'] == 'light':
        await handle_light(reader, writer)

async def start_server():
    server = await asyncio.start_server(handle_conn, HOST, PORT)
    addr = server.sockets[0].getsockname()

    print(f'Socket server started @ {addr}')

    async with server: await server.serve_forever()

def main():
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print('\nShutting down...')
        exit()

if __name__ == '__main__':
    main()
