# -*- coding: utf-8 -*-
import sys

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr
import webbrowser

import smtplib
import csv
from os.path import basename
from apscheduler.schedulers.background import BackgroundScheduler


from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

import poplib

from MAILTRY import Ui_MainWindow
from Connect import Ui_Connect

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp

sched = BackgroundScheduler()
sched.start()


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

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

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    name = u''
    passw = u''
    smtp_ = u''
    pop_ = u''
    smtp_port = 0
    pop_port = 0
    auto_reply = u''
    s_state = 0
    p_state = 0
    newmail_state = 0
    newmail_time = 1
    autore_state = 0
    old_mail_count = 0
    timer_interval = 0
    tray_icon = 0
    flag = 0

    def __init__( self ):
        QtWidgets.QMainWindow.__init__( self )
        Ui_MainWindow.__init__( self )
        Ui_Connect.__init__(self)
        self.setupUi( self )
        self.initInfo()
        #新邮件检查时间间隔:  值 * 60s = 值(分钟)
        self.timer_interval = self.checkTime.value() * 60
        #托盘图标
        self.tray_icon = QSystemTrayIcon(self)

        # 双击复原，单击隐藏
        self.tray_icon.activated.connect(self.trayClick)
        #右键菜单
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.show()

    def trayClick(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
        else:
            self.hide()

    def sendMail(self):
        userlist = []
        from_addr = (self.fromaddr.toPlainText())
        to_addr = (self.toaddr.toPlainText().split(','))
        i = 0

        for i in range(len(to_addr)):
            if to_addr[i] == '':
                del to_addr[i]

        if not len(to_addr):
            return

        with open('data/RecentConnect.csv') as f:
            f_csv = csv.reader(f)
            header = next(f_csv)
            for rows in f_csv:
                if rows[0] != '':
                    userlist.append(str(rows[0]))
            f.close()

        with open('data/RecentConnect.csv', 'a', newline='') as k:
            k_csv = csv.writer(k)
            for i in range(len(to_addr)):
                flag = 1
                for j in range(len(userlist)):
                    if to_addr[i] == userlist[j]:
                        flag = 0
                        break
                if flag:
                    #userlist.append(str(to_addr[i]))
                    k_csv.writerow([str(to_addr[i])])
            k.close()


        title = (self.title.toPlainText())
        password = self.passw
        content0 = (self.content.toPlainText())
        smtp_server = self.smtp_
        signedname = u'女仆酱'

        if signedname != '':
            content = u'%s \n-----%s' % (content0, signedname)
        else:
            content = content0

        if self.s_ssl_check.checkState():
            if self.smtp_port == 587 or self.smtp_port == 465:
                server = smtplib.SMTP(smtp_server, self.smtp_port)
                server.starttls()
            else:
                return
        else:
            if self.smtp_port == 25:
                server = smtplib.SMTP(smtp_server, self.smtp_port)
            else:
                return

        msg = MIMEMultipart()

        msg['From'] = _format_addr('女仆酱 <%s>' % from_addr)
        msg['To'] = _format_addr('Target')
        msg['Subject'] = Header('%s' % title, 'utf-8').encode()

        # 正文
        msg.attach(MIMEText('%s' % content, 'plain', 'utf-8'))

        way = (self.attach.toPlainText())

        for i in range(len(way)):
            if way[i] != '':
                base = basename(way[i])

                contype = 'application/octet-stream'  # 自动推导文件类型
                maintype, subtype = contype.split('/', 1)

                with open(u'%s' % way[i], 'rb') as f:
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

        self.progressBar.setValue(20)
        #server.set_debuglevel(1)
        server.login(from_addr, password)
        self.progressBar.setValue(40)
        server.sendmail(from_addr, to_addr, msg.as_string())
        self.progressBar.setValue(60)
        server.quit()
        self.progressBar.setValue(100)


    def loop(self,msg,num):
        for header in ['From', 'To', 'Date' ,'Subject']:
            value = msg.get(header,'')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
        self.listMail.addItem(u'%d mail: < %s >' % (num, value))

    def listAllMail(self):
        self.listMail.clear()
        email = self.name
        password = self.passw
        pop3_server = self.pop_

        if self.p_ssl_check.checkState():
            if self.pop_port == 995:
                server = poplib.POP3_SSL(pop3_server, self.pop_port)
            else:
                return
        else:
            if self.pop_port == 110:
                server = poplib.POP3(pop3_server, self.pop_port)
            else:
                return

        # 调试信息
        # server.set_debuglevel(1);
        # 用户验证
        server.user(email)
        server.pass_(password)
        # list()返回所有邮件的编号:
        resp, mails, octects = server.list()
        index = len(mails)
        k = index
        # 获取最新一封邮件, 注意索引号从1开始:
        while k > 0:
            resp, lines, octets = server.retr(k)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            self.loop(msg,k)
            self.readspeed.setValue(100-int(k/index)*100)
            k -= 1
        server.quit()

        #self.listMail.addItem('a')

    def print_mail(self, msg,indent=0):
        if indent == 0:
            for header in ['From', 'To', 'Date', 'Subject']:
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
                self.mailcontent.append(u'%s%s: %s' % ( '  ' * indent, header, value))
            self.mailcontent.append(u'\nContent: ')

        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                fname = part.get_filename()
                if fname:
                    fpath = u'Filerecv/%s' % (fname)
                    data = part.get_payload(decode=True)
                    with open(fpath, 'wb') as file_save:
                        file_save.write(data)
                        file_save.close()
                self.print_mail(part, indent + 1)
        else:
            content_type = msg.get_content_type()
            #if content_type == 'text/plain':
            #    content = msg.get_payload(decode=True)
            #    charset = guess_charset(msg)
            #    if charset:
            #        content = content.decode(charset)
            #        self.mailcontent.append(u'%s%s' % ('  ' * indent, content))
            if content_type == 'text/html':
                content = msg.get_payload(decode=True)
                charset = guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                    self.mailcontent.append(content)
            else:
                return

    def showMailDetail(self):
        if not self.listMail.currentItem():
            return
        cur = str(self.listMail.currentItem().text())
        f = int(cur.split()[0])
        self.mailcontent.clear()
        email = self.name
        password = self.passw
        pop3_server = self.pop_

        if self.p_ssl_check.checkState():
            if self.pop_port == 995:
                server = poplib.POP3_SSL(pop3_server, self.pop_port)
            else:
                return
        else:
            if self.pop_port == 110:
                server = poplib.POP3(pop3_server, self.pop_port)
            else:
                return
        self.readspeed.setValue(20)
        # 调试信息
        #server.set_debuglevel(1)
        # 用户验证
        server.user(email)
        server.pass_(password)
        self.readspeed.setValue(40)
        # 获取最新一封邮件, 注意索引号从1开始:
        resp, lines, octects = server.retr(f)
        # 可以获得整个邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        # 稍后解析出邮件:
        msg = Parser().parsestr(msg_content)
        self.readspeed.setValue(60)
        self.print_mail(msg)
        server.quit()
        self.readspeed.setValue(100)

    def saveInfo(self):
        self.name = str(self.username.text())
        self.passw = str(self.password.text())
        self.smtp_ = str(self.smtpedit.text())
        self.pop_ = str(self.pop3edit.text())
        self.smtp_port = int(self.s_port.text())
        self.pop_port = int(self.p_port.text())
        self.s_state = self.s_ssl_check.checkState()
        self.p_state = self.p_ssl_check.checkState()
        self.newmail_state = self.NewMailCheck.checkState()
        self.newmail_time = self.checkTime.value()
        self.autore_state = self.autoreplay_check.checkState()
        self.auto_reply = str(self.autoreply.toPlainText())
        self.fromaddr.setPlainText(self.name)
        with open('data/userinfo.csv','w',newline='') as f:
            f_csv = csv.writer(f)
            headers = ['name','password','smtp','s_check','s_port','pop','p_check','p_port','mailcheck','mailcheck_time','auto_check','auto reply']
            rows = [(self.name, self.passw,
                     self.smtp_, self.s_ssl_check.checkState(), self.smtp_port,
                     self.pop_, self.p_ssl_check.checkState(), self.pop_port,
                     self.NewMailCheck.checkState(), self.newmail_time,
                     self.autoreplay_check.checkState(), self.auto_reply)]
            f_csv.writerow(headers)
            f_csv.writerows(rows)
            f.close()

    def saveCancel(self):
        self.username.setText(self.name)
        self.password.setText(self.passw)
        self.smtpedit.setText(self.smtp_)
        self.pop3edit.setText(self.pop_)
        self.s_port.setText(str(self.smtp_port))
        self.p_port.setText(str(self.pop_port))
        self.s_ssl_check.setChecked(bool(self.s_state))
        self.p_ssl_check.setChecked(bool(self.p_state))
        self.NewMailCheck.setChecked(bool(self.newmail_state))
        self.checkTime.setValue(self.newmail_time)
        self.autoreplay_check.setChecked(bool(self.autore_state))
        self.autoreply.setPlainText(self.auto_reply)
        self.fromaddr.setPlainText(self.name)

    def initInfo(self):
        with open('data/userinfo.csv') as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)
            for row in f_csv:
                self.name = row[0]
                self.username.setText(row[0])
                if self.name != '':
                    self.fromaddr.setPlainText(self.name)
                self.passw = row[1]
                self.password.setText(row[1])
                self.smtp_ = row[2]
                self.smtpedit.setText(row[2])
                self.s_state = int(row[3])
                self.s_ssl_check.setChecked(int(row[3]))
                self.smtp_port = int(row[4])
                self.s_port.setText(row[4])
                self.pop_ = row[5]
                self.pop3edit.setText(row[5])
                self.p_state = int(row[6])
                self.p_ssl_check.setChecked(int(row[6]))
                self.pop_port = int(row[7])
                self.p_port.setText(row[7])
                self.newmail_state = int(row[8])
                self.NewMailCheck.setChecked(int(row[8]))
                self.newmail_time = int(row[9])
                self.checkTime.setValue(int(row[9]))
                self.autore_state = int(row[10])
                self.autoreplay_check.setChecked(int(row[10]))
                self.auto_reply = row[11]
                self.autoreply.setPlainText(row[11])
            f.close()

        with open('data/mailCount.csv') as h:
            h_csv = csv.reader(h)
            headers = next(h_csv)
            for row in h_csv:
                self.old_mail_count = int(row[0])
            h.close()

    def showConnect(self):
        self.toaddr.clear()
        new_window = Connect()
        new_window.show()
        new_window.showConnect()
        new_window.exec_()
        self.toaddr.setPlainText(new_window.getRecv())

    def MailCheck(self):

        if self.NewMailCheck.checkState() == 0:
            return

        email = self.name
        password = self.passw
        pop3_server = self.pop_

        if self.p_ssl_check.checkState():
            if self.pop_port == 995:
                server = poplib.POP3_SSL(pop3_server, self.pop_port)
            else:
                return
        else:
            if self.pop_port == 110:
                server = poplib.POP3(pop3_server, self.pop_port)
            else:
                return

        # 用户验证
        server.user(email)
        server.pass_(password)
        # list()返回所有邮件的编号:
        resp, mails, octects = server.list()
        index = len(mails)
        if index > self.old_mail_count:

            self.tray_icon.showMessage(
                "新邮件提醒",
                "你有%d封新邮件"%(index - self.old_mail_count),
                QSystemTrayIcon.Information,
                1000
            )
            k = index
            if self.autore_state != 0:
                while k > self.old_mail_count:
                    resp, lines, octets = server.retr(k)
                    msg_content = b'\r\n'.join(lines).decode('utf-8')
                    msg = Parser().parsestr(msg_content)
                    self.loop1(msg)
                    k -= 1
            self.old_mail_count = index
            with open('data/mailCount.csv','w',newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(['count:'])
                f_csv.writerows([('%d' % self.old_mail_count)])
                f.close()
            server.quit()
        else:
            server.quit()
        return

    def loop1(self, msg):
        for header in ['From', 'To', 'Date', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'From':
                    hdr, addr = parseaddr(value)
        return self.autoReply(addr)

    def autoReply(self, to_addr):
        if self.autore_state != 0:
            from_addr = self.name
            title = u'自动回复'
            password = self.passw
            content0 = self.auto_reply
            smtp_server = self.smtp_
            signedname = u'女仆酱'
            if self.s_ssl_check.checkState():
                if self.smtp_port == 587 or self.smtp_port == 465:
                    server = smtplib.SMTP(smtp_server, self.smtp_port)
                    server.starttls()
                else:
                    return
            else:
                if self.smtp_port == 25:
                    server = smtplib.SMTP(smtp_server, self.smtp_port)
                else:
                    return

            msg = MIMEText(u'%s'%content0, 'plain', 'utf-8')

            msg['From'] = _format_addr('女仆酱 <%s>' % from_addr)
            msg['To'] = _format_addr('Target<%s>' % to_addr)
            msg['Subject'] = Header('%s' % title, 'utf-8').encode()
            # server.set_debuglevel(1)
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
            return True
        else:
            return False

    def showFiles(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self,
                                               r'添加附件',
                                               r'F:\Python',
                                               r'All Files(*.*)') #word(*.doc);;All Files(*.*)
        self.attach.appendPlainText(fileName[0])


class Connect(QtWidgets.QDialog, Ui_Connect):
    Reciever = u''
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_Connect.__init__(self)
        self.setupUi(self)

    def showConnect(self):
        with open('data/RecentConnect.csv') as f:
            f_csv = csv.reader(f)
            header = next(f_csv)
            for rows in f_csv:
                if rows[0] != '':
                    self.listConnect.addItem(str(rows[0]))
            f.close()

    def choice(self):
        if not self.listConnect.currentItem():
            return
        cur = self.listConnect.currentItem().text()
        self.connectChoice.appendPlainText(u'%s,' % cur)

    def decide(self):
        if self.connectChoice.toPlainText() == '':
            return
        temp = self.connectChoice.toPlainText().split('\n')
        self.Reciever = u''.join(temp)
        self.close()

    def getRecv(self):
        return self.Reciever




if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sched.add_job(window.MailCheck, 'interval', seconds=window.timer_interval)
    sys.exit(app.exec_())