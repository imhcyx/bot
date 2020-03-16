from model import User, Group, Teach, Nine
import random
import re

class BaseCommand:
    def __init__(self):
        self.format = ''
        self.desc = ''
        self.help = ''
        self.level = 0

    def handler(self, cm, arg, user):
        return ''

class AdminCommand(BaseCommand):
    def __init__(self):
        self.format = '...'
        self.desc = '管理员命令'
        self.help = "只有True Administrator才能执行的命令（"
        self.level = 5
    
    def handler(self, cm, arg, user):
        if user.id == 907308901:
            return 'not implemented'
        else:
            return "权限不足"

class CallmeCommand(BaseCommand):
    def __init__(self, dbsess):
        self.format = '<nickname>'
        self.desc = '设置称谓'
        self.help = '设置琪露诺对我的称谓为<nickname>。'
        self.level = 0
        self._dbsess = dbsess

    def handler(self, cm, arg, user):
        if len(arg) != 2:
            return "参数个数不正确"
        user.name = arg[1]
        self._dbsess.commit()
        return "好的，%s！本姑娘以后就这么称呼你啦~" % user.title()

class HelpCommand(BaseCommand):
    def __init__(self):
        self.format = '[<cmd>]'
        self.desc = '查看帮助'
        self.help = "查看命令列表或指定命令的帮助。"
        self.level = 0

    def handler(self, cm, arg, user):
        if len(arg) == 1:
            s = "命令列表：\n"
            for (k, v) in cm.command_iter():
                s += "%s %s\n" % (k, v.desc)
            s += "\n使用.cirno.help <cmd>查看命令具体帮助，<cmd>可省略\".cirno.\"。"
            return s
        elif len(arg) == 2:
            s = arg[1]
            if not s.startswith('.cirno'):
                s = '.cirno.' + s
            cmd = cm.command(s)
            if cmd:
                return "%s %s\n权限要求：%d\n%s" % (s, cmd.format, cmd.level, cmd.help)
            else:
                return "未知命令%s" % s
        else:
            return "参数个数不正确"

class MeCommand(BaseCommand):
    def __init__(self):
        self.format = ''
        self.desc = '我的信息'
        self.help = '查看我的信息'
        self.level = 0

    def handler(self, cm, arg, user):
        return "你好，%s！\n你的权限等级为%d。" % (user.title(), user.level)

class TeachCommand(BaseCommand):
    def __init__(self, dbsess):
        self.format = '<question> <answer>'
        self.desc = '问答教学'
        self.help = "教琪露诺回答问题吧！当提问内容为<question>时，琪露诺会回答<answer>。"
        self.level = 1
        self._dbsess = dbsess

    def handler(self, cm, arg, user):
        if len(arg) != 3:
            return "参数个数不正确"
        teach = Teach(uid=user.id, question=arg[1], answer=arg[2])
        self._dbsess.add(teach)
        self._dbsess.commit()
        return "琪露诺成功记住了问题的答案！问答编号为%d。" % teach.id

class TeachDeleteCommand(BaseCommand):
    def __init__(self, dbsess):
        self.format = '<id>'
        self.desc = '删除问答'
        self.help = "根据给定的问答编号<id>删除问答内容。"
        self.level = 4
        self._dbsess = dbsess

    def handler(self, cm, arg, user):
        if len(arg) != 2:
            return "参数个数不正确"
        try:
            id = int(arg[1])
            teach = self._dbsess.query(Teach).filter_by(id=id).one()
            self._dbsess.delete(teach)
            self._dbsess.commit()
            return "删除成功！"
        except:
            return "查询失败"

class TeachQueryCommand(BaseCommand):
    def __init__(self, dbsess):
        self.format = '<id>'
        self.desc = '查询问答'
        self.help = "根据给定的问答编号<id>查询问答内容。"
        self.level = 4
        self._dbsess = dbsess

    def handler(self, cm, arg, user):
        if len(arg) != 2:
            return "参数个数不正确"
        try:
            id = int(arg[1])
            teach = self._dbsess.query(Teach).filter_by(id=id).one()
            return "查询结果：\n%d. 用户%d的问答\n问：%s\n答：%s" % (
                teach.id, teach.uid, teach.question, teach.answer)
        except:
            return "查询失败"

class TeachSearchCommand(BaseCommand):
    def __init__(self, dbsess):
        self.format = '<keyword>'
        self.desc = '搜索问答内容'
        self.help = "根据给定的关键字<keyword>查询问答内容。"
        self.level = 4
        self._dbsess = dbsess

    def handler(self, cm, arg, user):
        if len(arg) != 2:
            return "参数个数不正确"
        try:
            kwlike = '%%%s%%' % arg[1]
            teaches = self._dbsess.query(Teach).filter(Teach.question.like(kwlike)).all()
            s = "问题包含\"%s\"的记录：" % arg[1]
            for teach in teaches:
                s += "\n%d. 用户%d的问答\n问：%s\n答：%s" % (
                    teach.id, teach.uid, teach.question, teach.answer)
            teaches = self._dbsess.query(Teach).filter(Teach.answer.like(kwlike)).all()
            s += "\n---------------------"
            s += "\n回答包含\"%s\"的记录：" % arg[1]
            for teach in teaches:
                s += "\n%d. 用户%d的问答\n问：%s\n答：%s" % (
                    teach.id, teach.uid, teach.question, teach.answer)
            return s
        except:
            return "查询失败"

def parse_command(msg):
    arg = []
    word = ''
    quote = False
    for i in range(len(msg)):
        c = msg[i]
        if c == '"':
            quote = not quote
        elif c == ' ' and not quote:
            if word != '':
                arg.append(word)
                word = ''
        else:
            word += c
    if word != '':
        arg.append(word)
    return arg

class CommandManager:
    def __init__(self, dbsess):
        self._commands = {
            '.cirno.admin': AdminCommand(),
            '.cirno.callme': CallmeCommand(dbsess),
            '.cirno.help': HelpCommand(),
            '.cirno.me': MeCommand(),
            '.cirno.teach': TeachCommand(dbsess),
            '.cirno.teach.delete': TeachDeleteCommand(dbsess),
            '.cirno.teach.query': TeachQueryCommand(dbsess),
            '.cirno.teach.search': TeachSearchCommand(dbsess),
        }
        self._dbsess = dbsess

    def register_command(self, name, cmd):
        self._commands[name] = cmd

    def command(self, name):
        return self._commands.get(name)

    def command_iter(self):
        for (k, v) in self._commands.items():
            yield(k, v)

    def handle_message(self, msg, uid):
        if msg.startswith('.cirno'):
            arg = parse_command(msg)
            if arg[0] == '.cirno':
                return "我是天才少女琪露诺！输入.cirno.help查看帮助信息"
            cmd = self._commands.get(arg[0])
            if cmd:
                query = self._dbsess.query(User).filter_by(id=uid)
                user = None
                if query.count() == 0:
                    user = User(id=uid, level=1)
                    self._dbsess.add(user)
                    self._dbsess.commit()
                else:
                    user = query.one()
                if user.level >= cmd.level:
                    return cmd.handler(self, arg, user)
                else:
                    return "你没有使用该命令的权限。"
            else:
                return "未知命令%s" % arg[0]
        else:
            teaches = self._dbsess.query(Teach).filter_by(question=msg).all()
            if len(teaches) > 0:
                teach = random.choice(teaches)
                return teach.answer
            elif len(msg) < 50: # nine calculation
                max = -1
                for x in re.findall(r'[0-9]+', msg, re.M):
                    i = int(x)
                    if i > max:
                        max = i
                nine = self._dbsess.query(Nine).filter_by(number=max)
                if nine.count() > 0:
                    return nine.one().answer
