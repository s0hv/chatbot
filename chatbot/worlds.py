# Based on the implementation from parlai.chat_service.tasks.chatbot.worlds.py
import random

from parlai.core.agents import create_agent_from_shared
from parlai.core.worlds import World
from parlai.tasks.blended_skill_talk.worlds import get_contexts_data


class ConversationBotTaskWorld(World):
    """
    The overworld and default task for this service
    """
    MAX_AGENTS = 1
    MODEL_KEY = 'blender_400M'

    def __init__(self, opt, agent, bot):
        self.agent = agent
        self.episodeDone = False
        self.first_interaction = True
        self.model = bot

        if 'datatype' not in opt:
            opt['datatype'] = 'train'

        # Must not include these as it would make the start of the conversation
        # unnatural to the user
        opt['include_initial_utterances'] = False

        self.contexts_data = get_contexts_data(opt)

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

    def get_context(self):
        random.seed()
        p = random.choice(self.contexts_data)
        return p[0]

    def load_persona(self):
        persona = self.get_context()
        self.model.observe({'id': 'context', 'text': persona, 'episode_done': False})
        print("===persona====")
        print("~~~~~~~~~~~")
        print(persona)

    def parley(self):
        if self.first_interaction:
            self.load_persona()
            self.first_interaction = False

        a = self.agent.act()
        if a is not None:
            if '[DONE]' in a['text']:
                self.episodeDone = True
                return 'default'
            elif '[RESET]' in a['text']:
                self.model.reset()
                self.agent.observe({"text": "[History Cleared]", "episode_done": False})
                self.load_persona()

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
