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





@app.route("/", methods=["GET"])
def index():
    token = request.args.get('token')
    return  asyncio.run(getFile(token))


if __name__ == '__main__':
    from waitress import serve
    app.debug = False
    port = 5000
    serve(app, port=port)