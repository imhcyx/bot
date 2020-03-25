import random
import re
import time

from command import CommandManager, AdminManager
from model import User, Group, Teach, Nine
from config import cfg

class BaseFilter:
    def handle(self, msg):
        pass

class FilterList(BaseFilter):
    def __init__(self, subfilters=[]):
        self.__subfilters = subfilters
    
    def handle(self, msg):
        for filter in self.__subfilters:
            if filter.handle(msg):
                break

class AccessLimitFilter(BaseFilter):
    def __init__(self, subfilters=[]):
        self.__subfilters = subfilters
    
    def handle(self, msg):
        if msg.user.runtime.access_cooldown:
            if not msg.user.runtime.access_cooldown_prompted:
                msg.user.runtime.access_cooldown_prompted = True
                msg.reply('%s，你说话太快了，请稍后再试。' % msg.user.title)
            return True
        for filter in self.__subfilters:
            if filter.handle(msg):
                ts = msg.user.runtime.timestamps
                ts = [time.time()] + ts[:9]
                msg.user.runtime.timestamps = ts
                # 10 accesses in 10 seconds
                if len(ts) == 10 and (ts[9] - ts[0]) < 10:
                    msg.user.runtime.access_cooldown = True
                    msg.user.runtime.access_cooldown_prompted = False
                    def func():
                        msg.user.runtime.access_cooldown = False
                    msg.cirno.set_timeout(30, func)
                break

class AdminFilter(BaseFilter):
    def __init__(self):
        self.__am = AdminManager()
    
    def handle(self, msg):
        if msg.text.startswith('!') and msg.user.id == cfg['admin_id']:
            result = self.__am.handle(msg)
            if result or result == '':
                msg.reply(result)
                return True

class CommandFilter(BaseFilter):
    def __init__(self):
        self.__cm = CommandManager()
    
    def handle(self, msg):
        if msg.text.startswith('.cirno'): 
            result = self.__cm.handle(msg)
            if result or result == '':
                msg.reply(result)
                return True

class QAFilter(BaseFilter):
    def handle(self, msg):
        teaches = msg.cirno.sess.query(Teach).filter_by(question=msg.text).all()
        if len(teaches) > 0:
            teach = random.choice(teaches)
            msg.reply(teach.answer)
            return True

class NineFilter(BaseFilter):
    def handle(self, msg):
        text = msg.text
        max = -1
        for x in re.findall(r'[0-9]+', text, re.M):
            i = int(x)
            if i > max:
                max = i
        if max >= 0:
            ans = self.find_answer(max, msg.cirno.sess)
            if ans:
                msg.reply('%d = %s' % (max, ans))
                return True
    
    def find_answer(self, num, sess):
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
    def handle(self, msg):
        if '琪露诺' in msg.text and random.random() < 0.5:
            msg.reply('嗯？谁在叫本姑娘？')
            return True

default_filters = FilterList([
    AdminFilter(),
    AccessLimitFilter([
        CommandFilter(),
        QAFilter(),
        SpecialFilter(),
        NineFilter(),
    ]),
])