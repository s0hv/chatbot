# Based on the implementation from parlai.chat_service.tasks.chatbot.worlds.py

from parlai.core.agents import create_agent_from_shared
from parlai.core.worlds import World


class ConversationBotTaskWorld(World):
    """
    The overworld and default task for this service
    """
    MAX_AGENTS = 1
    MODEL_KEY = 'blender_400M'

    def __init__(self, opt, agent, bot):
        self.agent = agent
        self.episodeDone = False
        self.model = bot

    @staticmethod
    def generate_world(opt, agents):
        if opt['models'] is None:
            raise RuntimeError("Model must be specified")
        return ConversationBotTaskWorld(
            opt,
            agents[0],
            create_agent_from_shared(
                opt['shared_bot_params'][ConversationBotTaskWorld.MODEL_KEY]
            ),
        )

    @staticmethod
    def assign_roles(agents):
        agents[0].disp_id = 'ChatbotAgent'

    def parley(self):
        a = self.agent.act()
        if a is not None:
            if '[DONE]' in a['text']:
                self.episodeDone = True
            elif '[RESET]' in a['text']:
                self.model.reset()
                self.agent.observe({"text": "[History Cleared]", "episode_done": False})
            else:
                print("===act====")
                print(a)
                print("~~~~~~~~~~~")
                self.model.observe(a)
                response = self.model.act()
                print("===response====")
                print(response)
                print("~~~~~~~~~~~")
                self.agent.observe(response)

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.agent.shutdown()
