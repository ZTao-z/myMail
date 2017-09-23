# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr

import smtplib
from os.path import basename

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

from_addr = input('From: ')
password = "zsfjcucyqmrmbadb"

#逗号分隔收信人
to_addr = input('To: ')
smtp_server = input('SMTP server: ')

title = input('Title: ')
content0 = input('Content: ')
signedname = u'女仆酱' #input('signedname: ')

if signedname != '':
    content = u'%s \n-----%s' % (content0, signedname)
else:
    content = content0

msg = MIMEMultipart()

msg['From'] = _format_addr('女仆酱 <%s>' % from_addr)
msg['To'] = _format_addr('你 <%s>' % to_addr)
msg['Subject'] = Header('%s' % title, 'utf-8').encode()

#正文
msg.attach(MIMEText('%s' % content, 'plain', 'utf-8'))


#发送附件

num = int(input('number of objects: '))
while num > 0:
    way = input('object: ')
    if way != '':
        base = basename(way)

        contype = 'application/octet-stream' #自动推导文件类型
        maintype, subtype = contype.split('/', 1)

        with open(u'%s' % way, 'rb') as f:
            mime = MIMEBase(maintype, subtype)

            mime.add_header('Content-Disposition', 'attachment', filename=('gbk', '', base))
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')

            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            msg.attach(mime)
            f.close()
    num = num - 1


server = smtplib.SMTP(smtp_server, 587)
server.starttls()
server.set_debuglevel(1)
server.login(from_addr, password)
server.sendmail(from_addr, [to_addr], msg.as_string())
server.quit()
