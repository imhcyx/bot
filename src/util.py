def parsecommand(msg):
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

def cqunescape(s):
    s = s.replace('&amp;', '&')
    s = s.replace('&#91;', '[')
    s = s.replace('&#93;', ']')
    s = s.replace('&#44;', ',')
    return s