class BaseCommand:
    def __init__(self):
        self.format = ''
        self.desc = ''
        self.help = ''

    def handler(self, cm, arg, uid):
        return ''

class AdminCommand(BaseCommand):
    def __init__(self):
        self.format = '...'
        self.desc = '管理员命令'
        self.help = "只有True Administrator才能执行的命令（"
    
    def handler(self, cm, arg, uid):
        if uid == 907308901:
            return 'not implemented'
        else:
            return "权限不足"

class HelpCommand(BaseCommand):
    def __init__(self):
        self.format = '[<cmd>]'
        self.desc = '查看帮助'
        self.help = "查看命令列表或指定命令的帮助"

    def handler(self, cm, arg, uid):
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
                return "%s %s\n%s" % (s, cmd.format, cmd.help)
            else:
                return "未知命令%s" % s
        else:
            return "参数个数不正确"

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
    def __init__(self):
        self._commands = {
            '.cirno.admin': AdminCommand(),
            '.cirno.help': HelpCommand()
        }
    
    def register_command(self, name, cmd):
        self._commands[name] = cmd

    def command(self, name):
        return self._commands.get(name)

    def command_iter(self):
        for (k, v) in self._commands.items():
            yield(k, v)

    def handle_command(self, msg, uid):
        arg = parse_command(msg)
        if arg[0] == '.cirno':
            return "我是天才少女琪露诺，输入.cirno.help查看帮助信息"
        cmd = self._commands.get(arg[0])
        if cmd:
            return cmd.handler(self, arg, uid)
        else:
            return "未知命令%s" % arg[0]
