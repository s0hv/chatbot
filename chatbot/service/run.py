# Based on the parlai Browser chat runner
import parlai.chat_service.utils.config as config_utils
from parlai.core.params import ParlaiParser

from chatbot.service.manager import ConversationServiceManager

SERVICE_NAME = 'Conversation'


def setup_args():
    parser = ParlaiParser(False, False)
    parser.add_parlai_data_path()
    parser.add_chatservice_args()
    parser_grp = parser.add_argument_group('Websocket conversation service')
    parser_grp.add_argument(
        '--port', default=36000, type=int, help='Port to run the websocket chat server'
    )
    return parser.parse_args()


def run(opt):
    """
    Run BrowserManager.
    """
    opt['service'] = SERVICE_NAME
    manager = ConversationServiceManager(opt)
    try:
        manager.start_task()
    finally:
        manager.shutdown()


if __name__ == '__main__':
    opt = setup_args()
    config_path = opt.get('config_path')
    config = config_utils.parse_configuration_file(config_path)
    opt.update(config['world_opt'])
    opt['config'] = config
    run(opt)
