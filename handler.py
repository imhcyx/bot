from command import CommandManager

class MsgHandler:
    def _send_response(self, event, resp):
        pass

    def handle_message(self, hm, event):
        uid = event.get('user_id')
        msg = event.get('message')
        if msg.startswith('.cirno'):
            resp = hm.cmdmanager().handle_command(msg, uid)
            return self._send_response(event, resp)

class PrivateMsgHandler(MsgHandler):
    def _send_response(self, event, resp):
        return {
            'action': 'send_private_msg',
            'params': {
                'user_id': event['user_id'],
                'message': resp
            }
        }

class GroupMsgHandler(MsgHandler):
    def _send_response(self, event, resp):
        return {
            'action': 'send_group_msg',
            'params': {
                'group_id': event['group_id'],
                'message': resp
            }
        }

class HandlerManager:
    def __init__(self):
        self._msghandlers = {
            'private': PrivateMsgHandler(),
            'group': GroupMsgHandler()
        }
        self._fallbackmsghandler = MsgHandler()
        self._cm = CommandManager()
    
    def cmdmanager(self):
        return self._cm

    def handle_event(self, event):
        if event.get('post_type') == 'message':
            h = self._msghandlers.get(event.get('message_type'),
                self._fallbackmsghandler)
            return h.handle_message(self, event)