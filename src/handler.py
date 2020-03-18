from filter import FilterManager
from model import User, Group

class HandlerHelper:
    def __init__(self, dbsess, send_f, newtask_f):
        self._dbsess = dbsess
        self._send_f = send_f
        self._newtask_f = newtask_f
        self._fm = FilterManager(self)
    
    def dbsess(self):
        return self._dbsess

    def send(self, resp):
        self._send_f(resp)

    def new_task(self, task):
        self._newtask_f(task)

    def fm(self):
        return self._fm

    def handle_event(self, event):
        if event.get('post_type') == 'message':
            return self.handle_message(event)

    def handle_message(self, event):
        msg = event.get('message')
        uid = event.get('user_id')
        gid = event.get('group_id')
        resp = self._fm.handle(msg, uid, gid)
        if resp:
            if gid:
                self.send_group_msg(gid, resp)
            else:
                self.send_private_msg(uid, resp)

    def send_msg(self, uid, gid, resp):
        if gid:
            self.send_group_msg(gid, resp)
        else:
            self.send_private_msg(uid, resp)

    def send_private_msg(self, uid, resp):
        self.send({
            'action': 'send_private_msg',
            'params': {
                'user_id': uid,
                'message': resp
            }
        })

    def send_group_msg(self, gid, resp):
        self.send({
            'action': 'send_group_msg',
            'params': {
                'group_id': gid,
                'message': resp
            }
        })
    
    def get_user_by_id(self, id):
        sess = self._dbsess
        query = sess.query(User).filter_by(id=id)
        if query.count() == 0:
            user = User(id=id, level=1)
            sess.add(user)
            sess.commit()
        else:
            user = query.one()
        return user
    
    def get_group_by_id(self, id):
        sess = self._dbsess
        query = sess.query(Group).filter_by(id=id)
        if query.count() == 0:
            group = Group(id=id)
            sess.add(group)
            sess.commit()
        else:
            group = query.one()
        return group
