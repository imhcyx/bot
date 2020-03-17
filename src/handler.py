from filter import FilterManager

class MsgHandler:
    def _send_response(self, event, resp):
        pass

    def handle_message(self, hm, event):
        msg = event.get('message')
        uid = event.get('user_id')
        gid = event.get('group_id')
        resp = hm.filtman().handle(msg, uid, gid)
        if resp:
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
    def __init__(self, dbsess):
        self._msghandlers = {
            'private': PrivateMsgHandler(),
            'group': GroupMsgHandler(),
        }
        self._fm = FilterManager(dbsess)
    
    def filtman(self):
        return self._fm

    def handle_event(self, event):
        if event.get('post_type') == 'message':
            h = self._msghandlers.get(event.get('message_type'))
            if h:
                return h.handle_message(self, event)