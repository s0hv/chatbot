import json
import os
import threading
import traceback
from typing import Optional

import websocket
from fastapi import FastAPI, Body
from pydantic import BaseModel

SHARED = {}


def setup_interactive(ws):
    # Save websockets instance for global usage
    SHARED['ws'] = ws


# Contains the newest message. Could be improved by using a threading queue
new_message = None
message_available = threading.Event()


def on_open(_):
    SHARED['ws_open'] = True


def on_error(_, error):
    traceback.print_exc(error)


def on_close(_):
    print('Connection closed')


def on_message(_, message):
    """
    Saves the incoming message to the global message variable
    """
    incoming_message = json.loads(message)
    global new_message
    new_message = incoming_message['text']
    message_available.set()


def handle_startup():
    # Possibility of infinite loop
    send_message('begin')


def send_message(msg: str) -> Optional[str]:
    """
    Send a message to the websocket and return the response

    Args:
        msg: The message to be sent

    Returns:
        The response message or None if it was not defined
    """
    print(f'Sending message {msg}')
    data = {
        'text': msg
    }
    json_data = json.dumps(data)
    SHARED['ws'].send(json_data)
    message_available.wait()
    new_msg = new_message
    message_available.clear()

    if '"begin"' in new_msg:
        print('Handling startup')
        handle_startup()

        return send_message(msg)

    return new_msg


app = FastAPI()


class Message(BaseModel):
    """
    Defines a body that contains a message
    """
    message: str


@app.post('/interact')
def interact(message: Message = Body(...)):
    print(message)
    return {
        'response': send_message(message.message)
    }


@app.post('/reset')
def reset_interaction():
    send_message('[RESET]')


@app.on_event('shutdown')
def shutdown_event():
    # Close websocket on shutdown
    SHARED['ws'].close()


@app.on_event('startup')
def startup_event():
    # Open websocket on startup
    port = os.environ.get('WS_PORT', 36000)

    print("Connecting to port: ", port)
    ws = websocket.WebSocketApp(
        "ws://localhost:{}/websocket".format(port),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open
    setup_interactive(ws)
    threading.Thread(target=ws.run_forever, daemon=True).start()
