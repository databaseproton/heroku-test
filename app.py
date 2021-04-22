from flask import Flask
from flask import request, jsonify
from flask import send_file
from telethon import TelegramClient, events, sync, utils
from telethon.sessions import StringSession
import threading
import asyncio
from flask import Response
import json
import io
import os
from fast import download_file
from base64 import b64decode
from nacl.secret import SecretBox
import math
import time

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
session_name= os.environ.get('SESSION_NAME')



app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)



def download_progress_callback(downloaded_bytes, total_bytes):
    print(downloaded_bytes)




async def getFile(token):
    client = TelegramClient(StringSession(session_name), api_id, api_hash, loop=loop)
    await client.connect()
    channel_username = 'ECEguide'
    message_dump = await client.get_messages(channel_username, limit=200)
    for message in message_dump:
        print(message)
        if message.media is not None and message.id == 86264:
            size = message.file.size
            offset = 0
            limit = size
            dc_id, location = utils.get_input_location(message.media)
            print(location, flush=True)
            print(message)
            string_out = io.BytesIO()
            ##await client.download_file(location, string_out, part_size_kb=512, progress_callback=download_progress_callback)
            await download_file(client, message.document, string_out, progress_callback=download_progress_callback)
            string_out.seek(0)
            return send_file(
                string_out,
                as_attachment=True,
                attachment_filename=message.file.name,
                mimetype='application/pdf'
                )


def decryptor(encrypted_string):
    secret_key = 'LSXny9anYA3kN2x2ck68tLcVwKWCRMEZ'
    encrypted = b64decode(encrypted_string).decode("utf-8") 
    encrypted = encrypted.split(':')
    # We decode the two bits independently
    nonce = b64decode(encrypted[0])
    encrypted = b64decode(encrypted[1])
    # We create a SecretBox, making sure that out secret_key is in bytes
    box = SecretBox(bytes(secret_key, encoding='utf8'))
    decrypted = box.decrypt(encrypted, nonce).decode('utf-8')
    return decrypted


@app.route("/", methods=["GET"])
def index():
    group = decryptor(request.args.get('group'))
    noteid = request.args.get('noteid')
    expire = int(decryptor(request.args.get('expire')))
    current_time = math.floor(int(time.time()))
    if current_time < expire:
        return  asyncio.run(getFile(token))
    else:
        return "Link Has Expired"

if __name__ == '__main__':
    from waitress import serve
    app.debug = False
    port = 5000
    serve(app, port=port)