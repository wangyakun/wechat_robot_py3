#coding=utf8
__author__ = 'WYK'

import os
import time
import logging
import requests
import itchat
# 关于itchat问题：AttributeError: 'HTMLParser' object has no attribute 'unescape'  解决：https://github.com/littlecodersh/ItChat/pull/932/files
# 关于itchat问题：itchat.auto_login登录问题（1.3.10存在,  1.2不存在）  解决：https://github.com/littlecodersh/ItChat/issues/970 ：
#       在 itchat/components/login.py 的 login() 函数中，在进入 while not isLoggedIn 循环前加了一个sleep
import threading
import datetime
import random
import traceback

import importlib, sys
importlib.reload(sys)

help_info = '''“delay close” 关闭延时回复
“delay open” 打开延时回复
“disturb close” 关闭打扰模式
“disturb open” 打开打扰模式
“close” 关闭机器人
“open” 打开机器人
“close XXX” 针对XXX屏蔽自动回复
“open XXX” 针对XXX打开自动回复
“list” 查看屏蔽列表
“closelist XXX,XXX,XXX” 对多人屏蔽自动回复
“auther” 作者信息'''

# KEY = '8edce3ce905a4c1dbb965e6b35c3834d'
KEY = 'f26276bebeba492ab763e83e89c511d0'

record_log = True
auto_rep = True
no_auto_rep_list = []
time_interval = True
append_disturb = True
last_repl_time = datetime.datetime.now()
pic_repl_list = [u'[发呆]', u'[呲牙]', u'[愉快]', u'[偷笑]', u'[憨笑]', u'[抠鼻]', u'[坏笑]', u'[阴险]', u'[嘿哈]', u'[奸笑]', u'[机智]']

class LOG:
    def __init__(self):
        self.LOG_HOME = r'D:\log\wxRobotLog'
        self.NO_AUTO_REP_LIST = r'D:\log\noAutoRepList'
        if not os.path.exists(self.LOG_HOME):
            os.makedirs(self.LOG_HOME)
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename=os.path.join(self.LOG_HOME, 'wxRobot.log'),
            filemode='w')
        self.set_file('default')

    def set_file(self, user):
        self.user = user

    def log(self, message):
        if not record_log:
            return
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(now)
        print(message)
        logging.info(message)
        with open(os.path.join(self.LOG_HOME, self.user + '.log'), 'a') as f:
            f.write(now)
            f.write('\n')
            f.write(message)
            f.write('\n')

    def save_no_auto_rep_list(self):
        global no_auto_rep_list
        no_auto_rep_list = list(set(no_auto_rep_list))
        with open(self.NO_AUTO_REP_LIST, 'w') as f:
            f.write(str(no_auto_rep_list))

    def load_no_auto_rep_list(self):
        global no_auto_rep_list
        if not os.path.exists(self.NO_AUTO_REP_LIST):
            return False
        with open(self.NO_AUTO_REP_LIST, 'r') as f:
            no_auto_rep_list = list(f.read())

logger = LOG()

def ctl_msg(msg):
    global auto_rep, no_auto_rep_list, time_interval, append_disturb, record_log
    if msg['ToUserName'] != 'filehelper':
        return False
    print('!!!this is admin!!!')
    print('msg:')
    print(msg['Text'])

    if msg['Text'] == 'open':
        auto_rep = True
        itchat.send(u'机器人已开启', 'filehelper')
    elif msg['Text'].startswith('open '):
        user = msg['Text'][5:]
        if user in no_auto_rep_list:
            no_auto_rep_list.remove(user)
        itchat.send(u'机器人已对 %s 开启' % user, 'filehelper')
    elif msg['Text'] == 'close':
        auto_rep = False
        itchat.send(u'机器人已关闭', 'filehelper')
    elif msg['Text'].startswith('closelist '):
        close_list = msg['Text'][11:].split(',')
        no_auto_rep_list.extend(close_list)
        logger.save_no_auto_rep_list()
        itchat.send(u'机器人已对列表 %s 关闭' % close_list, 'filehelper')
    elif msg['Text'].startswith('close '):
        user = msg['Text'][6:]
        if user not in no_auto_rep_list:
            no_auto_rep_list.append(user)
            logger.save_no_auto_rep_list()
        itchat.send(u'机器人已对 %s 关闭' % user, 'filehelper')
    elif msg['Text'] == 'list':
        print(no_auto_rep_list)
        itchat.send(u'已关闭列表：', 'filehelper')
        itchat.send(','.join(no_auto_rep_list), 'filehelper')
    elif msg['Text'].startswith('delay '):
        ctrl = msg['Text'][6:]
        if ctrl == 'open':
            time_interval = True
            itchat.send(u'延时回复已开启', 'filehelper')
        elif ctrl == 'close':
            time_interval = False
            itchat.send(u'延时回复已关闭', 'filehelper')
    elif msg['Text'].startswith('disturb '):
        ctrl = msg['Text'][8:]
        if ctrl == 'open':
            append_disturb = True
            itchat.send(u'打扰模式已开启', 'filehelper')
        elif ctrl == 'close':
            append_disturb = False
            itchat.send(u'打扰模式已关闭', 'filehelper')
    elif msg['Text'].startswith('log '):
        ctrl = msg['Text'][4:]
        if ctrl == 'open':
            record_log = True
            itchat.send(u'后台记录日志已开启', 'filehelper')
        elif ctrl == 'close':
            record_log = False
            itchat.send(u'后台记录日志已关闭', 'filehelper')
    elif msg['Text'] == 'auther':
        itchat.send(u'wechat-robot auther:君莫思归', 'filehelper')
    elif msg['Text'] == 'help':
        itchat.send(help_info, 'filehelper')
    return True

# #图灵机器人已失效
# def get_response(msg, userid = 'wechat-robot'):
#     # 这里我们就像在“3. 实现最简单的与图灵机器人的交互”中做的一样
#     # 构造了要发送给服务器的数据
#     apiUrl = 'http://www.tuling123.com/openapi/api'
#     data = {
#         'key'    : KEY,
#         'info'   : msg,
#         'userid' : userid,
#     }
#     try:
#         r = requests.post(apiUrl, data=data).json()
#         # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
#         return r.get('text')
#     # 为了防止服务器没有正常响应导致程序异常退出，这里用try-except捕获了异常
#     # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
#     except:
#         # 将会返回一个None
#         return

#使用青云客机器人回复，回复速度会慢一些
def get_response(msg, userid = 'wechat-robot'):
    # 这里我们就像在“3. 实现最简单的与图灵机器人的交互”中做的一样
    # 构造了要发送给服务器的数据
    apiUrl = 'http://api.qingyunke.com/api.php'
    params = {
        'key': 'free',
        'appid': '0',
        'msg': msg
    }
    try:
        r = requests.get(apiUrl, params=params).json()
        return r.get('content')
    except:
        # 将会返回一个None
        return

@itchat.msg_register(itchat.content.RECORDING)
def voice_reply(msg):
    to_user_nickname = msg['User'].get('NickName', 'unknown')
    if not auto_rep or (to_user_nickname != 'unknown' and to_user_nickname in no_auto_rep_list):
        return
    if time_interval:
        sec = 6
        print("recive voice. sec", sec)
        def repl():
            itchat.send(u'手机听筒坏了，听不到语音', msg['FromUserName'])
            print("repled")
        t = threading.Timer(sec, repl)
        t.start()
    else:
        return u'手机听筒坏了，听不到语音'

@itchat.msg_register(itchat.content.PICTURE)
def picture_reply(msg):
    if time_interval:
        sec = 2
        print("recive image. sec", sec)
        def repl():
            itchat.send(random.choice(pic_repl_list), msg['FromUserName'])
            print("repled")
        t = threading.Timer(sec, repl)
        t.start()
    else:
        return random.choice(pic_repl_list)
        
# 这里是我们在“1. 实现微信消息的获取”中已经用到过的同样的注册方法
@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    global logger, no_auto_rep_list, last_repl_time
    if ctl_msg(msg):
        return
    to_user_nickname = msg['User'].get('NickName', 'unknown')
    if not auto_rep or (to_user_nickname != 'unknown' and to_user_nickname in no_auto_rep_list):
        return

    # 为了保证在图灵Key出现问题的时候仍旧可以回复，这里设置一个默认回复
    defaultReply = 'I received: ' + msg['Text']
    # 如果图灵Key出现问题，那么reply将会是None
    reply = get_response(msg['Text'], to_user_nickname)
    # a or b的意思是，如果a有内容，那么返回a，否则返回b
    # 有内容一般就是指非空或者非None，你可以用`if a: print('True')`来测试
    try:
        logger.set_file(to_user_nickname)
        logger.log('%s:%s' % (to_user_nickname, msg['Text']))
        logger.log('rep:%s' % reply if reply else defaultReply)
    except Exception as e:
        print(str(e))
        print("Exception ignored!!!!")
        
    last_repl_time = datetime.datetime.now()
    if append_disturb:#todo:性能
        sec = 600
        def repl():
            if append_disturb and last_repl_time + datetime.timedelta(minutes=9) < datetime.datetime.now():
                itchat.send(u'怎么不说话了', msg['FromUserName'])
                print("disturb %s" % msg['FromUserName'])
        t = threading.Timer(sec, repl)
        t.start()

    if time_interval:
        sec = min(len(reply or defaultReply), 50)
        print("sec", sec)
        def repl():
            itchat.send(reply or defaultReply, msg['FromUserName'])
            print("repled")
        t = threading.Timer(sec, repl)
        t.start()
    else:
        return reply or defaultReply

def main():
    # 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
    #itchat.auto_login(hotReload=True, enableCmdQR=True)
    itchat.auto_login(hotReload=True, enableCmdQR=False)
    itchat.send('Hello, filehelper', toUserName='filehelper')
    # print itchat.get_chatrooms(update=True)
    itchat.run()

if __name__ == '__main__':
    logger.load_no_auto_rep_list()
    # while True:
    try:
        main()
        print('end!!!!!')
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        time.sleep(5)
    # print('!!!!!!restart!!!!!!!!')
    print('!!!!!!exit!!!!!!!!')

