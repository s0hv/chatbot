from parlai.chat_service.services.browser_chat import run
import parlai.chat_service.utils.config as config_utils

if __name__ == '__main__':
    opt = run.setup_args()
    config_path = opt.get('config_path')
    config = config_utils.parse_configuration_file(config_path)
    opt.update(config['world_opt'])
    opt['config'] = config
    run.run(opt)
