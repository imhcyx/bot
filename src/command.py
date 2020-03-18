from model import User, Group, Teach, Nine
from status import status
from util import parsecommand, cqunescape
from util import SystemTask

class BaseCommand:
    def __init__(self, format, desc, help, level, parser=parsecommand):
        self.format = format
        self.desc = desc
        self.help = help
        self.level = level
        self.parser = parser

    def handle(self, arg, user, group):
        return ''

class CallmeCommand(BaseCommand):
    def __init__(self, hh):
        BaseCommand.__init__(
            self,
            format = '<nickname>',
            desc = '设置称谓',
            help = '设置琪露诺对我的称谓为<nickname>。',
            level = 0
        )
        self._hh = hh

    def handle(self, arg, user, group):
        if len(arg) != 2:
            return "参数个数不正确"
        user.name = arg[1]
        self._hh.dbsess().commit()
        return "好的，%s！本姑娘以后就这么称呼你啦~" % user.title()

class GpCommand(BaseCommand):
    def __init__(self, hh):
        BaseCommand.__init__(
            self,
            format = '<stmt> ...',
            desc = 'PARI/GP计算器',
            help = '在PARI/GP中执行表达式',
            level = 1,
            parser = lambda x: x.split(' ')
        )
        self._hh = hh
        self._blacklist = [
            'default',
            'extern',
            'system',
        ]

    def handle(self, arg, user, group):
        if len(arg) < 2:
            return "参数个数不正确"
        stmt_r = ' '.join(arg[1:])
        stmt = cqunescape(stmt_r)
        for word in self._blacklist:
            if word in stmt:
                return '禁止包含%s' % word
        uid = user.id
        gid = group.id if group else None
        path = '/tmp/bot.gp'
        try:
            with open(path, 'w') as f:
                f.write("default(\"secure\", 1)\n")
                f.write(stmt)
        except:
            return '文件操作失败'
        task = SystemTask(
            uid=uid,
            gid=gid,
            callback=lambda s:self._hh.send_msg(
                uid, gid, "用户：%s\n表达式：%s\n输出：\n%s" % (user.title(), stmt_r, s)),
            cmd='chroot --userspec=nobody / gp -q %s' % path
        )
        self._hh.new_task(task)
        return False


class HelpCommand(BaseCommand):
    def __init__(self, cm):
        BaseCommand.__init__(
            self,
            format = '[<cmd>]',
            desc = '查看帮助',
            help = "查看命令列表或指定命令的帮助。",
            level = 0
        )
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
        BaseCommand.__init__(
            self,
            format = '',
            desc = '我的信息',
            help = '查看我的信息',
            level = 0
        )

    def handle(self, arg, user, group):
        return "你好，%s！\n你的权限等级为%d。" % (user.title(), user.level)

class TeachCommand(BaseCommand):
    def __init__(self, hh):
        BaseCommand.__init__(
            self,
            format = '<question> <answer>',
            desc = '问答教学',
            help = "教琪露诺回答问题吧！当提问内容为<question>时，琪露诺会回答<answer>。",
            level = 1
        )
        self._hh = hh

    def handle(self, arg, user, group):
        if len(arg) != 3:
            return "参数个数不正确"
        teach = Teach(uid=user.id, question=arg[1], answer=arg[2])
        self._hh.dbsess().add(teach)
        self._hh.dbsess().commit()
        return "琪露诺成功记住了问题的答案！问答编号为%d。" % teach.id

class TeachDeleteCommand(BaseCommand):
    def __init__(self, hh):
        BaseCommand.__init__(
            self,
            format = '<id>',
            desc = '删除问答',
            help = "根据给定的问答编号<id>删除问答内容。",
            level = 4
        )
        self._hh = hh

    def handle(self, arg, user, group):
        if len(arg) != 2:
            return "参数个数不正确"
        try:
            id = int(arg[1])
            teach = self._hh.dbsess().query(Teach).filter_by(id=id).one()
            self._hh.dbsess().delete(teach)
            self._hh.dbsess().commit()
            return "删除成功！"
        except:
            return "查询失败"

class TeachQueryCommand(BaseCommand):
    def __init__(self, hh):
        BaseCommand.__init__(
            self,
            format = '<id>',
            desc = '查询问答',
            help = "根据给定的问答编号<id>查询问答内容。",
            level = 4
        )
        self._hh = hh

    def handle(self, arg, user, group):
        if len(arg) != 2:
            return "参数个数不正确"
        try:
            id = int(arg[1])
            teach = self._hh.dbsess().query(Teach).filter_by(id=id).one()
            return "查询结果：\n%d. 用户%d的问答\n问：%s\n答：%s" % (
                teach.id, teach.uid, teach.question, teach.answer)
        except:
            return "查询失败"

class TeachSearchCommand(BaseCommand):
    def __init__(self, hh):
        BaseCommand.__init__(
            self,
            format = '<keyword>',
            desc = '搜索问答内容',
            help = "根据给定的关键字<keyword>查询问答内容。",
            level = 4
        )
        self._hh = hh

    def handle(self, arg, user, group):
        if len(arg) != 2:
            return "参数个数不正确"
        try:
            kwlike = '%%%s%%' % arg[1]
            teaches = self._hh.dbsess().query(Teach).filter(Teach.question.like(kwlike)).all()
            s = "问题包含\"%s\"的记录：" % arg[1]
            for teach in teaches:
                s += "\n%d. 用户%d的问答\n问：%s\n答：%s" % (
                    teach.id, teach.uid, teach.question, teach.answer)
            teaches = self._hh.dbsess().query(Teach).filter(Teach.answer.like(kwlike)).all()
            s += "\n---------------------"
            s += "\n回答包含\"%s\"的记录：" % arg[1]
            for teach in teaches:
                s += "\n%d. 用户%d的问答\n问：%s\n答：%s" % (
                    teach.id, teach.uid, teach.question, teach.answer)
            return s
        except:
            return "查询失败"

class CommandManager:
    def __init__(self, hh):
        self._commands = {
            '.cirno.callme': CallmeCommand(hh),
            '.cirno.gp': GpCommand(hh),
            '.cirno.help': HelpCommand(self),
            '.cirno.me': MeCommand(),
            '.cirno.teach': TeachCommand(hh),
            '.cirno.teach.delete': TeachDeleteCommand(hh),
            '.cirno.teach.query': TeachQueryCommand(hh),
            '.cirno.teach.search': TeachSearchCommand(hh),
        }
        self._hh = hh

    def register_command(self, name, cmd):
        self._commands[name] = cmd

    def command(self, name):
        return self._commands.get(name)

    def command_iter(self):
        for (k, v) in self._commands.items():
            yield(k, v)

    def handle(self, msg, user, group):
        cmdname = msg.split(' ')[0]
        if cmdname == '.cirno':
            return "我是天才少女琪露诺！输入.cirno.help查看帮助信息"
        cmd = self._commands.get(cmdname)
        if cmd:
            if user.level >= cmd.level:
                arg = cmd.parser(msg)
                return cmd.handle(arg, user, group)
            else:
                return "你没有使用该命令的权限。"
        else:
            return "未知命令%s" % cmdname

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
        else:
            return 'Invalid argument format'

class LevelAdminCommand(BaseAdminCommand):
    def __init__(self, hh):
        self._hh = hh
    
    def handle(self, arg, user, group):
        if len(arg) == 2:
            try:
                uid = int(arg[1])
                u = self._hh.get_user_by_id(uid)
                return 'Level: %d' % u.level
            except:
                return 'Failed'
        elif len(arg) == 3:
            try:
                uid = int(arg[1])
                level = int(arg[2])
                u = self._hh.get_user_by_id(uid)
                u.level = level
                self._hh.dbsess().commit()
                return 'OK'
            except:
                return 'Failed'
        else:
            return 'Invalid argument format'

class SendAdminCommand(BaseAdminCommand):
    def __init__(self, hh):
        self._hh = hh
    
    def handle(self, arg, user, group):
        if len(arg) < 3:
            return 'Invalid argument format'
        try:
            uid = int(arg[1])
            msg = ' '.join(arg[2:])
            self._hh.send_private_msg(uid, msg)
            return 'OK'
        except:
            return 'Failed'

class SendgroupAdminCommand(BaseAdminCommand):
    def __init__(self, hh):
        self._hh = hh
    
    def handle(self, arg, user, group):
        if len(arg) < 3:
            return 'Invalid argument format'
        try:
            gid = int(arg[1])
            msg = ' '.join(arg[2:])
            self._hh.send_group_msg(gid, msg)
            return 'OK'
        except:
            return 'Failed'

class StatusAdminCommand(BaseAdminCommand):
    def handle(self, arg, user, group):
        s = 'STATUS'
        for (k, v) in status.items():
            s += "\n%s: %s" %(k, repr(v))
        return s

class SystemAdminCommand(BaseAdminCommand):
    def __init__(self, hh):
        self._hh = hh
    
    def handle(self, arg, user, group):
        if len(arg) > 1:
            uid = user.id
            gid = group.id if group else None
            cmd_r = ' '.join(arg[1:])
            cmd = cqunescape(cmd_r)
            task = SystemTask(
                uid=uid,
                gid=gid,
                callback=lambda s:self._hh.send_msg(
                    uid, gid, "Command: %s\nResult:\n%s" % (cmd_r, s)),
                cmd=cmd
            )
            self._hh.new_task(task)
            return False
        else:
            return 'Invalid argument format'

class AdminManager:
    def __init__(self, hh):
        self._commands = {
            '.cirnoadmin.block': BlockAdminCommand(),
            '.cirnoadmin.level': LevelAdminCommand(hh),
            '.cirnoadmin.send': SendAdminCommand(hh),
            '.cirnoadmin.sendgroup': SendgroupAdminCommand(hh),
            '.cirnoadmin.status': StatusAdminCommand(),
            '.cirnoadmin.system': SystemAdminCommand(hh),
        }
        self._hh = hh
    
    def handle(self, msg, user, group):
        arg = msg.split(' ')
        if arg[0] == '.cirnoadmin':
            return 'Access confirmed'
        cmd = self._commands.get(arg[0])
        if cmd:
            return cmd.handle(arg, user, group)
            