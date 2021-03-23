import logging
import os
import sys
from pathlib import Path

# https://stackoverflow.com/a/30218825
# Add project directory to python path so local imports can be done
parent = Path(__file__).resolve().parents[1]
sys.path.append(str(parent))

# Clear default loggers. Must be done before importing parlai
logging.getLogger().handlers.clear()

# Create logs dir
logs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
if not os.path.exists(logs_path):
    os.mkdir(logs_path)

# Setup logging
logging.basicConfig(
    filename=os.path.join(logs_path, 'websocket.log'),
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG,
)

if __name__ == '__main__':
    from chatbot.service import run
    import parlai.chat_service.utils.config as config_utils

    opt = run.setup_args()
    config_path = opt.get('config_path')
    config = config_utils.parse_configuration_file(config_path)
    opt.update(config['world_opt'])
    opt['config'] = config
    run.run(opt)
