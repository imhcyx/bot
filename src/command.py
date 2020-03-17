from model import User, Group, Teach, Nine
from status import status
from util import parse_command

class BaseCommand:
    def __init__(self):
        self.format = ''
        self.desc = ''
        self.help = ''
        self.level = 0

    def handle(self, arg, user, group):
        return ''

class CallmeCommand(BaseCommand):
    def __init__(self, dbsess):
        self.format = '<nickname>'
        self.desc = '设置称谓'
        self.help = '设置琪露诺对我的称谓为<nickname>。'
        self.level = 0
        self._dbsess = dbsess

    def handle(self, arg, user, group):
        if len(arg) != 2:
            return "参数个数不正确"
        user.name = arg[1]
        self._dbsess.commit()
        return "好的，%s！本姑娘以后就这么称呼你啦~" % user.title()

class HelpCommand(BaseCommand):
    def __init__(self, cm):
        self.format = '[<cmd>]'
        self.desc = '查看帮助'
        self.help = "查看命令列表或指定命令的帮助。"
        self.level = 0
        self._cm = cm

    def handle(self, arg, user, group):
        if len(arg) == 1:
            s = "命令列表：\n"
            for (k, v) in self._cm.command_iter():
                s += "%s %s\n" % (k, v.desc)
            s += "\n使用.cirno.help <cmd>查看命令具体帮助，<cmd>可省略\".cirno.\"。"
            return s
        elif len(arg) == 2:
            s = arg[1]
            if not s.startswith('.cirno'):
                s = '.cirno.' + s
            cmd = self._cm.command(s)
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

    def handle(self, arg, user, group):
        return "你好，%s！\n你的权限等级为%d。" % (user.title(), user.level)

class TeachCommand(BaseCommand):
    def __init__(self, dbsess):
        self.format = '<question> <answer>'
        self.desc = '问答教学'
        self.help = "教琪露诺回答问题吧！当提问内容为<question>时，琪露诺会回答<answer>。"
        self.level = 1
        self._dbsess = dbsess

    def handle(self, arg, user, group):
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

    def handle(self, arg, user, group):
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

    def handle(self, arg, user, group):
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

    def handle(self, arg, user, group):
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

class CommandManager:
    def __init__(self, dbsess):
        self._commands = {
            '.cirno.callme': CallmeCommand(dbsess),
            '.cirno.help': HelpCommand(self),
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

    def handle(self, msg, user, group):
        arg = parse_command(msg)
        if arg[0] == '.cirno':
            return "我是天才少女琪露诺！输入.cirno.help查看帮助信息"
        cmd = self._commands.get(arg[0])
        if cmd:
            if user.level >= cmd.level:
                return cmd.handle(arg, user, group)
            else:
                return "你没有使用该命令的权限。"
        else:
            return "未知命令%s" % arg[0]

class BaseAdminCommand:
    def handle(self, arg, user, group):
        pass

class BlockAdminCommand(BaseAdminCommand):
    def handle(self, arg, user, group):
        if len(arg) == 1:
            return 'blocked' if status['block'] else 'unblocked'
        elif len(arg) == 2:
            if arg[1] == '0':
                status['block'] = False
                return 'OK'
            elif arg[1] == '1':
                status['block'] = True
                return 'OK'

class StatusAdminCommand(BaseAdminCommand):
    def handle(self, arg, user, group):
        s = 'STATUS'
        for (k, v) in status.items():
            s += "\n%s: %s" %(k, repr(v))
        return s

class AdminManager:
    def __init__(self, dbsess):
        self._commands = {
            '.cirnoadmin.block': BlockAdminCommand(),
            '.cirnoadmin.status': StatusAdminCommand(),
        }
        self._dbsess = dbsess
    
    def handle(self, msg, user, group):
        arg = msg.split(' ')
        if arg[0] == '.cirnoadmin':
            return 'Access confirmed'
        cmd = self._commands.get(arg[0])
        if cmd:
            return cmd.handle(arg, user, group)
            