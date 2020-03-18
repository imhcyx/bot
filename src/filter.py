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
    def __init__(self, hh):
        self._hh = hh
        self._am = AdminManager(hh)
    
    def filter(self, msg, user, group):
        if msg.startswith('.cirnoadmin') and user.id == cfg['admin_id']:
            return self._am.handle(msg, user, group)
        elif status['block']:
            return False # block all subsequent filters

class CommandFilter(BaseFilter):
    def __init__(self, hh):
        self._hh = hh
        self._cm = CommandManager(hh)
    
    def filter(self, msg, user, group):
        if msg.startswith('.cirno'): 
            return self._cm.handle(msg, user, group)

class QAFilter(BaseFilter):
    def __init__(self, hh):
        self._hh = hh
    
    def filter(self, msg, user, group):
        teaches = self._hh.dbsess().query(Teach).filter_by(question=msg).all()
        if len(teaches) > 0:
            teach = random.choice(teaches)
            return teach.answer

class NineFilter(BaseFilter):
    def __init__(self, hh):
        self._hh = hh
    
    def filter(self, msg, user, group):
        if len(msg) < 50:
            max = -1
            for x in re.findall(r'[0-9]+', msg, re.M):
                i = int(x)
                if i > max:
                    max = i
            if max > 9 or random.random() < 0.6: # trigger with probability for 0-9
                nine = self._hh.dbsess().query(Nine).filter_by(number=max)
                if nine.count() > 0:
                    return nine.one().answer

class FilterManager:
    def __init__(self, hh):
        self._hh = hh
        self._filters = [
            AdminFilter(hh),
            CommandFilter(hh),
            QAFilter(hh),
            NineFilter(hh),
        ]

    def handle(self, msg, uid, gid):
        user = self._hh.get_user_by_id(uid) if uid else None
        group = self._hh.get_group_by_id(gid) if gid else None
        for filter in self._filters:
            result = filter.filter(msg, user, group)
            if result:
                return result
            elif result == False:
                return None