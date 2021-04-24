# About
This is a system that can be used to integrate the [ParlAI BST model](https://parl.ai/projects/recipes/)
(or any other ParlAI model) into other systems relatively easy. It has been tested to work on Linux, 
but getting it to work on other systems should not take too much work.

The program consists of three different parts which allows the model to be loaded in memory at all times. 
The parts of the program are the WebSocket server, the API server and the command line script that can be used to interact with the model.
The interaction script depends on the API server which in turn depends on the WebSocket server,
so all three programs must be running in order to use the interaction script.

In addition to these a simple file watcher Node.js script is bundled along.
The script watches a file for changes and after each change it calls the interaction script.

# Installation
Download and install Python 3.8 or later from https://www.python.org/downloads/ or your package manager.  
After Python has installed, [create a virtual environment](https://docs.python.org/3/tutorial/venv.html)
named `venv` in the project folder (`install-services.sh` depends on this name).

## Installing requirements
Make sure the virtual environment that was installed is active.  
Then run `pip install -r requirements.txt` in this folder to install the required Python packages.
No errors should occur during this process.

## Installing systemd services
This step only works on Linux systems with systemd installed.
The `install-services.sh` is responsible for installing and starting systemd services
for both the websocket and API servers.
The name of the websocket service is `conversation-websocket.service`
and the API service is called `conversation-api.service`

By default, the services are enabled which means they are automatically started on boot.
This behavior can be stopped by calling `systemctl disable service-name` for both services.
The services can be manually controlled with the commands `systemctl start`, `systemctl stop` and `systemctl restart`.

## Installing Node.js (optional)
This step is only required for running the `integration.js` script.
Start by installing the latest Node.js LTS build from https://nodejs.org/en/download/ or your package manager of choice.
No other dependencies are required unless the script is required to start on boot.
If that is the case, pm2 must be installed with `npm i -g pm2`.

The `install-services.sh` script is able to configure pm2 automatically,
but in case manual configuration is required here is how it's done.

Copy pm2-ecosystem.example.json and name it whatever you like.  
In the file replace the values for the environment variables
`INTEGRATION_PATH`, `INTEGRATION_IN_FILE` and `INTEGRATION_OUT_FILE`.

`INTEGRATION_PATH` is the full path to the folder where `INTEGRATION_IN_FILE` is located at
and where `INTEGRATION_OUT_FILE` will be written to.  

`INTEGRATION_IN_FILE` is the name of the input file that the script watches.

`INTEGRATION_OUT_FILE` is the name of the file that the integration script writes to.

In order to start the script run `pm2 start "path/to/ecosystem.json"` and `pm2 save`.
If autostart on boot is required, run `pm2 startup` and follow the instructions it gives.


# Configuration
The configuration is done mostly through program arguments.
The model that is used is defined in `config.yml` though.
The model is set with the `model_file` key, and the default value is `zoo:blender/blender_400Mdistill/model`.

# Usage
In case the systemd services weren't installed,
the programs can be manually started with the following commands.

### WebSocket server
This program runs the WebSocket server on the specified port.  
`python server/ws.py --config-path config.yml --port 36000`  
For all available arguments run `python server/ws.py --help`

### API server
This program runs the API server on the specified port.  
`uvicorn server.client:app --port 8080`  
The environment variable WS_PORT is used to determine the port of the WebSocket server.
The default value for WS_PORT is 36000.

### Interact script
For interacting with the bot the `interact.py` script is used. <br/>
Simple usage consists of 
```
$ python interact.py -i "Hi, how are you?"
I am doing well. How about yourself? What is your favorite food? Mine is icecream.
```
where the response is printed to stdout by default.

All available arguments are listed below. They can also be viewed with `python interact.py --help`.
```
usage: interact.py [-h] --input INPUT [--output OUTPUT] [--reset] [--isfile] [--api-address API_ADDRESS]

Text to text conversation system

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Path to the input file or the input text. If a filename is given the --isfile argument must be set.
  --output OUTPUT, -o OUTPUT
                        Name of the output file. If not specified the output will be written to stdout.
  --reset, -r           If given resets the conversation before sending the message.
  --isfile, -if         If given treats the input as a filepath. The actual message will be read from the given file.
  --api-address API_ADDRESS, --api API_ADDRESS
                        Address of the API server. http://localhost:8080 by default.
```
