#!/bin/bash

# Make sure the script is run as root
if [ "$EUID" -eq 0 ]
  then echo "Please do not run this script as root"
  exit
fi


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

echo -e "${YELLOW}Creating systemd service for the websocket server. Systemd operations require sudo.${NC}
"
echo "$WS_SERVICE" | sudo tee "/etc/systemd/system/$WS_SERVICE_NAME" > /dev/null

echo -e "${GREEN}Systemd service for websocket server created successfully${NC}"

sudo systemctl daemon-reload
sudo systemctl start "$WS_SERVICE_NAME"
sudo systemctl enable "$WS_SERVICE_NAME"

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

echo "$API_SERVICE" | sudo tee "/etc/systemd/system/$API_SERVICE_NAME" > /dev/null

echo -e "${GREEN}Systemd service for API server created successfully${NC}"

sudo systemctl daemon-reload
sudo systemctl start "$API_SERVICE_NAME"
sudo systemctl enable "$API_SERVICE_NAME"

echo -e "${GREEN}API service enabled${NC}
"

PM2_ECOSYSTEM=pm2-generated-ecosystem.json

if test -f "$DIR/$PM2_ECOSYSTEM"; then
    echo "File $PM2_ECOSYSTEM already exists. Skipping pm2 ecosystem generation"
    exit 0
fi

read -p "Do you want to also install and set up autostart for the Node.js script (requires pm2) (y/n)? " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
  exit 0
fi


read -rp "What folder is the input file located at?
" INTEGRATION_PATH
echo

read -rp "What is the name of the input file (default text-in.txt)?
" INTEGRATION_IN_FILE
echo

read -rp "What should be the name of the output file (default text-out.txt)?
" INTEGRATION_OUT_FILE
echo

PM2_ENV="{
    \"name\": \"text-integration\",
    \"script\": \"$DIR/integration.js\",
    \"instances\": 1,
    \"autorestart\": true,
    \"env\": {
        \"INTEGRATION_PATH\": \"$INTEGRATION_PATH\",
        \"INTEGRATION_IN_FILE\": \"$INTEGRATION_IN_FILE\",
        \"INTEGRATION_OUT_FILE\": \"$INTEGRATION_OUT_FILE\"
    }
}
"


echo "$PM2_ENV" | (umask 133; cat > "$DIR/$PM2_ECOSYSTEM"; )
pm2 start "$DIR/$PM2_ECOSYSTEM"
pm2 save

echo "
${GREEN}pm2 ecosystem started. In order to configure autostart at boot run 'pm2 startup' and follow instructions${NC}"
