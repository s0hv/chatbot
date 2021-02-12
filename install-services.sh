#!/bin/bash

# ANSI colors
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
USERNAME="$( logname )"

echo "Script directory \"$DIR\"
User the script will be running as: $USERNAME
"

read -p "Do you want to continue with this configuration (y/n)? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
  exit 0
fi


WS_SERVICE_NAME="conversation-websocket.service"
WS_SERVICE="
[Unit]
Description=Websocket server for conversation bot

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
User=$USERNAME
Environment="PATH=$DIR/venv/bin"
WorkingDirectory=$DIR
ExecStart=$DIR/venv/bin/python $DIR/server/ws.py --config-path config.yml --port 36000
"

echo -e "${YELLOW}Creating systemd service for the websocket server${NC}
"
echo "$WS_SERVICE" | tee /etc/systemd/system/$WS_SERVICE_NAME > /dev/null

echo -e "${GREEN}Systemd service for websocket server created successfully${NC}"

systemctl daemon-reload
systemctl start $WS_SERVICE_NAME
systemctl enable $WS_SERVICE_NAME

echo -e "${GREEN}Websocket service enabled${NC}
"


API_SERVICE_NAME="conversation-api.service"
API_SERVICE="
[Unit]
Description=API server for conversation bot

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
User=$USERNAME
Environment="PATH=$DIR/venv/bin"
WorkingDirectory=$DIR
ExecStart=$DIR/venv/bin/uvicorn server.client:app --port 8080
"
echo -e "${YELLOW}Creating systemd service for the conversation API${NC}
"

echo "$API_SERVICE" | tee /etc/systemd/system/$API_SERVICE_NAME > /dev/null

echo -e "${GREEN}Systemd service for API server created successfully${NC}"

systemctl daemon-reload
systemctl start $API_SERVICE_NAME
systemctl enable $API_SERVICE_NAME

echo -e "${GREEN}API service enabled${NC}
"
