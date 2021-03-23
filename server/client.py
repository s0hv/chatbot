import asyncio
import json
import os
from typing import Optional

import websockets
from fastapi import FastAPI, Body
from pydantic import BaseModel

WS: Optional[websockets.WebSocketCommonProtocol] = None


async def handle_startup():
    # Possibility of infinite loop
    await send_message('begin')


async def send_message(msg: str) -> Optional[str]:
    """
    Send a message to the websocket and return the response

    Args:
        msg: The message to be sent

    Returns:
        The response message or None if it was not defined
    """
    if not (WS and WS.open):
        print('Reconnecting websocket')
        await connect_ws()

    print(f'Sending message {msg}')
    data = {
        'text': msg
    }
    json_data = json.dumps(data)
    await WS.send(json_data)
    try:
        resp = json.loads(await asyncio.wait_for(WS.recv(), 3))
    except asyncio.TimeoutError:
        return

    new_message = resp['text']

    return new_message


async def reset_conversation():
    """
    Reset the ongoing conversation if the websocket is open
    """
    if WS and WS.open:
        await send_message('[RESET]')


app = FastAPI()


class Message(BaseModel):
    """
    Defines a body that contains a message
    """
    message: str
    reset: Optional[bool]


@app.post('/interact')
async def interact(message: Message = Body(...)):
    print(message)
    if message.reset:
        await reset_conversation()

    return {
        'response': await send_message(message.message)
    }


@app.post('/reset')
async def reset_interaction():
    await reset_conversation()


@app.on_event('shutdown')
async def shutdown_event():
    # Close websocket on shutdown
    await WS.close()


@app.on_event('startup')
async def startup_event():
    try:
        await connect_ws()
    except OSError:
        print('Failed to connect to websocket on boot. Trying again on the next request')
        # Failed to connect. Ignore and connect later
        pass


async def connect_ws():
    global WS
    # Close existing connection
    if WS:
        await WS.close()

    # Open websocket on startup
    port = os.environ.get('WS_PORT', 36000)

    print("Connecting to port: ", port)
    ws = await websockets.connect('ws://localhost:{}/websocket'.format(port))
    WS = ws
    return ws
