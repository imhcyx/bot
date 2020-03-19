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
        if msg.startswith('!') and user.id == cfg['admin_id']:
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
                ans = self.find_answer(max)
                if ans:
                    return '%d = %s' % (max, ans)
    
    def find_answer(self, num):
        sess = self._hh.dbsess()
        # 1. direct answer
        query = sess.query(Nine).filter_by(number=num)
        if query.count() > 0:
            return query.one().answer
        # 2. sum of known answers
        if num < 10000000000:
            all = []
            cur = num
            while cur > 0:
                query = sess.query(Nine).filter(Nine.number<=cur).order_by(Nine.number.desc()).limit(1)
                if query.count() > 0:
                    a = query.one()
                    all.append(a.answer)
                    cur -= a.number
                else:
                    break
            if cur == 0:
                return '+'.join(all)

class SpecialFilter(BaseFilter):
    def __init__(self, hh):
        self._hh = hh
    
    def filter(self, msg, user, group):
        if '琪露诺' in msg and random.random() < 0.5:
            return '嗯？谁在叫本姑娘？'

class FilterManager:
    def __init__(self, hh):
        self._hh = hh
        self._filters = [
            AdminFilter(hh),
            CommandFilter(hh),
            QAFilter(hh),
            SpecialFilter(hh),
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