import random
import re

from command import CommandManager, AdminManager
from model import User, Group, Teach, Nine
from config import cfg
from status import status

class BaseFilter:
    def filter(self, msg, user, group):
        pass

class AdminFilter(BaseFilter):
    def __init__(self, dbsess):
        self._dbsess = dbsess
        self._am = AdminManager(dbsess)
    
    def filter(self, msg, user, group):
        if msg.startswith('.cirnoadmin') and user.id == cfg['admin_id']:
            return self._am.handle(msg, user, group)
        elif status['block']:
            return False # block all subsequent filters

class CommandFilter(BaseFilter):
    def __init__(self, dbsess):
        self._dbsess = dbsess
        self._cm = CommandManager(dbsess)
    
    def filter(self, msg, user, group):
        if msg.startswith('.cirno'): 
            return self._cm.handle(msg, user, group)

class QAFilter(BaseFilter):
    def __init__(self, dbsess):
        self._dbsess = dbsess
    
    def filter(self, msg, user, group):
        teaches = self._dbsess.query(Teach).filter_by(question=msg).all()
        if len(teaches) > 0:
            teach = random.choice(teaches)
            return teach.answer

class NineFilter(BaseFilter):
    def __init__(self, dbsess):
        self._dbsess = dbsess
    
    def filter(self, msg, user, group):
        if len(msg) < 50 and random.random() < 0.6:
            max = -1
            for x in re.findall(r'[0-9]+', msg, re.M):
                i = int(x)
                if i > max:
                    max = i
            nine = self._dbsess.query(Nine).filter_by(number=max)
            if nine.count() > 0:
                return nine.one().answer

class FilterManager:
    def __init__(self, dbsess):
        self._dbsess = dbsess
        self._filters = [
            AdminFilter(dbsess),
            CommandFilter(dbsess),
            QAFilter(dbsess),
            NineFilter(dbsess),
        ]
    
    def _get_user_by_id(self, id):
        query = self._dbsess.query(User).filter_by(id=id)
        if query.count() == 0:
            user = User(id=id, level=1)
            self._dbsess.add(user)
            self._dbsess.commit()
        else:
            user = query.one()
        return user
    
    def _get_group_by_id(self, id):
        query = self._dbsess.query(Group).filter_by(id=id)
        if query.count() == 0:
            group = Group(id=id)
            self._dbsess.add(group)
            self._dbsess.commit()
        else:
            group = query.one()
        return group

    def handle(self, msg, uid, gid):
        user = self._get_user_by_id(uid) if uid else None
        group = self._get_group_by_id(gid) if gid else None
        for filter in self._filters:
            result = filter.filter(msg, user, group)
            if result:
                return result
            elif result == False:
                return None