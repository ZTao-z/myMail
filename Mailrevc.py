# -*- coding: utf-8 -*-

from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

import poplib


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def print_mail(msg, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Date' ,'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                elif header == 'Date':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))

    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            fname = part.get_filename()
            content_type = part.get_content_type()
            if fname:
                fpath = u'F:/Python/Filerecv/%s' % (fname)
                data = part.get_payload(decode=True)
                with open(fpath, 'wb') as file_save:
                    file_save.write(data)
                    file_save.close()
            print_mail(part, indent + 1)
        pass
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
                print('%s%s' % ('  ' * indent, content))
        else:
            pass

email = input('email: ')
password = 'zsfjcucyqmrmbadb'
pop3_server = input('POP3 server: ')

#连接pop3服务器
server = poplib.POP3_SSL(pop3_server, 995)

#调试信息
#server.set_debuglevel(1);
#用户验证
server.user(email)
server.pass_(password)
# list()返回所有邮件的编号:
resp, mails, octects = server.list()
#print(mails)
# 获取最新一封邮件, 注意索引号从1开始:
index = len(mails)
while index > 30:
    resp, lines, octects = server.retr(index)
    # 可以获得整个邮件的原始文本:
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 稍后解析出邮件:

    msg = Parser().parsestr(msg_content)

    print_mail(msg)
    index = index - 1

server.quit()
