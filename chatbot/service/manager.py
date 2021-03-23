from typing import Any, Dict

from parlai.chat_service.services.websocket.websocket_manager import \
    WebsocketManager

from chatbot.agents import ConversationAgent


class ConversationServiceManager(WebsocketManager):
    def _create_agent(self, task_id, socketID):
        """
        Initialize an agent and return it.

        Called each time an agent is placed into a new task.

        :param task_id:
            string task identifier
        :param agent_id:
            int agent id
        """
        return ConversationAgent(self.opt, self, socketID, task_id)

    def _on_first_message(self, message: Dict[str, Any]):
        super()._on_first_message(message)

        # Force conversation to start on first message
        agent_id = message['sender']['id']
        agent_state = self.get_agent_state(agent_id)
        # If an agent is in a solo world, we can put a typing indicator
        # and mark the message as read
        agent = agent_state.get_active_agent()
        if len(agent.message_partners) == 0:
            self.handle_bot_read(agent.id)  # type: ignore
        agent.put_data(message)


def run(opt):
    """
    Run BrowserManager.
    """
    opt['service'] = 'Conversation'
    manager = ConversationServiceManager(opt)
    try:
        manager.start_task()
    finally:
        manager.shutdown()
