import json
import os
from typing import Optional

import websockets
from fastapi import FastAPI, Body
from pydantic import BaseModel

SHARED = {}


def setup_interactive(ws):
    # Save websockets instance for global usage
    SHARED['ws'] = ws


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
    ws = SHARED['ws']
    if not ws.open:
        print('Reconnecting websocket')
        ws = await connect_ws()

    print(f'Sending message {msg}')
    data = {
        'text': msg
    }
    json_data = json.dumps(data)
    await ws.send(json_data)
    resp = json.loads(await ws.recv())
    new_message = resp['text']

    if '"begin"' in new_message:
        print('Handling startup')
        await handle_startup()

        return await send_message(msg)

    return new_message


app = FastAPI()


class Message(BaseModel):
    """
    Defines a body that contains a message
    """
    message: str


@app.post('/interact')
async def interact(message: Message = Body(...)):
    print(message)
    return {
        'response': await send_message(message.message)
    }


@app.post('/reset')
async def reset_interaction():
    await send_message('[RESET]')


@app.on_event('shutdown')
async def shutdown_event():
    # Close websocket on shutdown
    await SHARED['ws'].close()


@app.on_event('startup')
async def startup_event():
    await connect_ws()


async def connect_ws():
    # Close existing connection
    if SHARED.get('ws'):
        await SHARED['ws'].close()

    # Open websocket on startup
    port = os.environ.get('WS_PORT', 36000)

    print("Connecting to port: ", port)
    ws = await websockets.connect('ws://localhost:{}/websocket'.format(port))
    setup_interactive(ws)
    return ws
