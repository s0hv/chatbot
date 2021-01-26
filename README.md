# Chatbot
A chatbot implementing a text-to-text system for use in Deep Speaking Avatar B.Sc. project.

# Installation
Run `pip install -r requirements.txt`<br/>
TODO: how to setup everything else

# Usage
The program consists of three different parts. 
The websocket server, the api server, and the command line app used to interact with the api.

To start the websocket server run `python ws.py --config-path config.yml --port 36000`

To start the api run `uvicorn server.client:app --port 8080`

For interacting with the bot the `interact.py` script is used. <br/>
Simple usage consists of 
```
(venv) [user@computer]$ python interact.py -i "Hi, how are you?"
i am doing well , thank you . what do you do for a living ? i work in it .
```
where the response is printed to the console by default.
