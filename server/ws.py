import logging
import os

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
    from parlai.chat_service.services.browser_chat import run
    import parlai.chat_service.utils.config as config_utils

    opt = run.setup_args()
    config_path = opt.get('config_path')
    config = config_utils.parse_configuration_file(config_path)
    opt.update(config['world_opt'])
    opt['config'] = config
    run.run(opt)
