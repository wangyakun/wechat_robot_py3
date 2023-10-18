# coding=utf8
__author__ = 'WYK'

import os
import time
import logging
import requests
import itchat
# 关于itchat问题：AttributeError: 'HTMLParser' object has no attribute 'unescape' （python>=3.9 存在） 解决：https://github.com/littlecodersh/ItChat/pull/932/files ：
#       在 itchat/utils.py 的 htmlParser = HTMLParser() 后面加:
#             if not hasattr(htmlParser, 'unescape'):
#                 import html
#                 htmlParser.unescape = html.unescape
# 关于itchat问题：itchat.auto_login登录问题（itchat 1.3.10存在,  1.2不存在）  解决：https://github.com/littlecodersh/ItChat/issues/970 ：
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
“set label close” 关闭【机器人自动回复】标签
“set label open” 打开【机器人自动回复】标签
“close” 关闭机器人自动回复
“open” 打开机器人自动回复
“set close XXX” 针对XXX强制关闭自动回复(XXX为昵称)
“set open XXX” 针对XXX强制打开自动回复
“set cancel XXX” 把XXX从自动回复列表中取消
“list” 查看自动回复列表（True：强制自动回复，False：强制不自动回复）
"status" 查看当前状态
“set closelist XXX,XXX,XXX” 对多人屏蔽自动回复
“auther” 作者信息'''

is_delay_rep = False
is_disturb = False
is_robot_label_display = True
last_repl_time = datetime.datetime.now()
pic_repl_list = [u'[发呆]', u'[呲牙]', u'[愉快]', u'[偷笑]', u'[憨笑]', u'[抠鼻]', u'[坏笑]', u'[阴险]', u'[嘿哈]',
                 u'[奸笑]', u'[机智]']


class LOG:
    def __init__(self):
        self.LOG_HOME = r'D:\log\wxRobotLog'
        self.is_record_log = True
        if not os.path.exists(self.LOG_HOME):
            os.makedirs(self.LOG_HOME)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=os.path.join(self.LOG_HOME, 'wxRobot.log'),
                            filemode='w')

    def log(self, message, user='default'):
        if not self.is_record_log:
            return
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(now)
        print(message)
        logging.info(message)
        with open(os.path.join(self.LOG_HOME, user + '.log'), 'a') as f:
            f.write(now)
            f.write('\n')
            f.write(message)
            f.write('\n')


class RepListManager:
    def __init__(self):
        self.is_defualt_auto_rep = False
        self.NO_AUTO_REP_LIST_FILE = r'D:\log\noAutoRepList'
        self.auto_rep_dict = {}

    def set_auto_rep(self, user, is_rep):
        if user is None:
            return
        self.auto_rep_dict[user] = is_rep
        self.save_no_auto_rep_list()

    def judge_auto_rep(self, user):
        return self.auto_rep_dict.get(user) if self.auto_rep_dict.get(user) is not None else self.is_defualt_auto_rep

    def remove_auto_rep(self, user):
        if user in self.auto_rep_dict:
            self.auto_rep_dict.pop(user)

    def save_no_auto_rep_list(self):
        with open(self.NO_AUTO_REP_LIST_FILE, 'w') as f:
            f.write(str(self.auto_rep_dict))

    def load_no_auto_rep_list(self):
        if not os.path.exists(self.NO_AUTO_REP_LIST_FILE):
            return False
        with open(self.NO_AUTO_REP_LIST_FILE, 'r') as f:
            self.auto_rep_dict = dict(eval(f.read()))


logger = LOG()
rep_mgr = RepListManager()

def msg_with_label(msg_text):
    if is_robot_label_display:
        msg_text = u'【机器人自动回复】' + msg_text
    return msg_text

def send_msg(msg_text, user):
    itchat.send(msg_with_label(msg_text), user)


def ctl_msg(msg_info):
    global logger, rep_mgr, is_delay_rep, is_disturb, is_robot_label_display
    if msg_info['ToUserName'] != 'filehelper':
        return False
    print('!!!this is admin!!!')
    print('msg:')
    print(msg_info['Text'])


    if msg_info['Text'] == 'open':
        rep_mgr.is_defualt_auto_rep = True
        send_msg(u'机器人已开启', 'filehelper')
    elif msg_info['Text'] == 'close':
        rep_mgr.is_defualt_auto_rep = False
        send_msg(u'机器人已关闭', 'filehelper')
    elif msg_info['Text'].startswith('set open '):
        user = msg_info['Text'][9:]
        rep_mgr.set_auto_rep(user, True)
        send_msg(u'机器人已对 %s 开启' % user, 'filehelper')
    elif msg_info['Text'].startswith('set close '):
        user = msg_info['Text'][10:]
        rep_mgr.set_auto_rep(user, False)
        send_msg(u'机器人已对 %s 关闭' % user, 'filehelper')
    elif msg_info['Text'].startswith('set openlist '):
        open_list = msg_info['Text'][14:].split(',')
        for user in open_list:
            rep_mgr.set_auto_rep(user, True)
        send_msg(u'机器人已对列表 %s 开启' % open_list, 'filehelper')
    elif msg_info['Text'].startswith('set closelist '):
        close_list = msg_info['Text'][15:].split(',')
        for user in close_list:
            rep_mgr.set_auto_rep(user, False)
        send_msg(u'机器人已对列表 %s 关闭' % close_list, 'filehelper')
    elif msg_info['Text'].startswith('set cancel '):
        user = msg_info['Text'][11:]
        rep_mgr.remove_auto_rep(user)
        send_msg(u'机器人已对 %s 从自动回复列表中删除' % user, 'filehelper')
    elif msg_info['Text'].startswith('set label '):
        ctrl = msg_info['Text'][10:]
        if ctrl == 'open':
            is_robot_label_display = True
            send_msg(u'机器人自动回复标签已开启', 'filehelper')
        elif ctrl == 'close':
            is_robot_label_display = False
            send_msg(u'机器人自动回复标签已关闭', 'filehelper')
    elif msg_info['Text'] == 'list':
        print(rep_mgr.auto_rep_dict)
        send_msg(u'自动回复列表：\n' + str(rep_mgr.auto_rep_dict), 'filehelper')
    elif msg_info['Text'] == 'status':
        rep_msg = "当前状态：\n" \
                  "机器人是否开启：%s\n" \
                  "自动回复标签是否开启：%s\n" \
                  "延时回复模式是否开启：%s\n" \
                  "打扰模式（自动回复“怎么不说话了”）是否开启：%s"
        send_msg(rep_msg % (rep_mgr.is_defualt_auto_rep, is_robot_label_display, is_delay_rep, is_disturb), 'filehelper')
    elif msg_info['Text'].startswith('delay '):
        ctrl = msg_info['Text'][6:]
        if ctrl == 'open':
            is_delay_rep = True
            send_msg(u'延时回复已开启', 'filehelper')
        elif ctrl == 'close':
            is_delay_rep = False
            send_msg(u'延时回复已关闭', 'filehelper')
    elif msg_info['Text'].startswith('disturb '):
        ctrl = msg_info['Text'][8:]
        if ctrl == 'open':
            is_disturb = True
            send_msg(u'打扰模式已开启', 'filehelper')
        elif ctrl == 'close':
            is_disturb = False
            send_msg(u'打扰模式已关闭', 'filehelper')
    elif msg_info['Text'].startswith('log '):
        ctrl = msg_info['Text'][4:]
        if ctrl == 'open':
            logger.is_record_log = True
            send_msg(u'后台记录日志已开启', 'filehelper')
        elif ctrl == 'close':
            logger.is_record_log = False
            send_msg(u'后台记录日志已关闭', 'filehelper')
    elif msg_info['Text'] == 'auther':
        send_msg(u'wechat-robot auther:君莫思归', 'filehelper')
    elif msg_info['Text'] == 'help':
        send_msg(help_info, 'filehelper')
    return True


# #图灵机器人已失效
# KEY = '8edce3ce905a4c1dbb965e6b35c3834d'
# KEY = 'f26276bebeba492ab763e83e89c511d0'
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

# 使用青云客机器人回复，回复速度会慢一些
def get_response(msg_text, userid='wechat-robot'):
    # 这里我们就像在“3. 实现最简单的与图灵机器人的交互”中做的一样
    # 构造了要发送给服务器的数据
    apiUrl = 'http://api.qingyunke.com/api.php'
    params = {
        'key': 'free',
        'appid': '0',
        'msg': msg_text
    }
    try:
        r = requests.get(apiUrl, params=params).json()
        return r.get('content')
    except:
        # 将会返回一个None
        return


@itchat.msg_register(itchat.content.RECORDING)
def voice_reply(msg_info):
    to_user_nickname = msg_info['User'].get('NickName')
    if not rep_mgr.judge_auto_rep(to_user_nickname):
        return
    if is_delay_rep:
        sec = 6
        print("recive voice. sec", sec)

        def repl():
            send_msg(u'手机听筒坏了，听不到语音', msg_info['FromUserName'])
            print("repled")

        t = threading.Timer(sec, repl)
        t.start()
    else:
        return msg_with_label(u'手机听筒坏了，听不到语音')


@itchat.msg_register(itchat.content.PICTURE)
def picture_reply(msg_info):
    to_user_nickname = msg_info['User'].get('NickName')
    if not rep_mgr.judge_auto_rep(to_user_nickname):
        return
    if is_delay_rep:
        sec = 2
        print("recive image. sec", sec)

        def repl():
            send_msg(random.choice(pic_repl_list), msg_info['FromUserName'])
            print("repled")

        t = threading.Timer(sec, repl)
        t.start()
    else:
        return msg_with_label(random.choice(pic_repl_list))


# 这里是我们在“1. 实现微信消息的获取”中已经用到过的同样的注册方法
@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg_info):
    global logger, rep_mgr, last_repl_time
    if ctl_msg(msg_info):
        return
    to_user_nickname = msg_info['User'].get('NickName')
    if not rep_mgr.judge_auto_rep(to_user_nickname):
        return

    # 为了保证在图灵Key出现问题的时候仍旧可以回复，这里设置一个默认回复
    defaultReply = 'I received: ' + msg_info['Text']
    # 如果图灵Key出现问题，那么reply将会是None
    reply = get_response(msg_info['Text'], to_user_nickname)
    # a or b的意思是，如果a有内容，那么返回a，否则返回b
    # 有内容一般就是指非空或者非None，你可以用`if a: print('True')`来测试
    try:
        logger.log('%s:%s' % (to_user_nickname, msg_info['Text']), to_user_nickname)
        logger.log('rep:%s' % reply if reply else defaultReply, to_user_nickname)
    except Exception as e:
        print(str(e))
        print("Exception ignored!!!!")

    last_repl_time = datetime.datetime.now()
    if is_disturb:
        sec = 600

        def repl():
            if is_disturb and last_repl_time + datetime.timedelta(minutes=9) < datetime.datetime.now():
                send_msg(u'怎么不说话了', msg_info['FromUserName'])
                print("disturb %s" % msg_info['FromUserName'])

        t = threading.Timer(sec, repl)
        t.start()

    if is_delay_rep:
        sec = min(len(reply or defaultReply), 50)
        print("sec", sec)

        def repl():
            send_msg(reply or defaultReply, msg_info['FromUserName'])
            print("repled")

        t = threading.Timer(sec, repl)
        t.start()
    else:
        return msg_with_label(reply or defaultReply)

@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_reply(msg):
    if msg.isAt:
        msg.user.send(u'@%s\u2005I received: %s' % (
            msg.actualNickName, msg.text))


def lc():
    send_msg('机器人后台-启动', 'filehelper')

def ec():
    send_msg('机器人后台-退出', 'filehelper')

def main():
    # 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
    # itchat.auto_login(hotReload=True, enableCmdQR=True)
    itchat.auto_login(hotReload=True, enableCmdQR=False, loginCallback=lc, exitCallback=ec)
    # print itchat.get_chatrooms(update=True)
    itchat.run()


if __name__ == '__main__':
    rep_mgr.load_no_auto_rep_list()
    # while True:
    try:
        main()
        print('end!!!!!')
    except Exception as e:
        print(traceback.format_exc())
        time.sleep(5)
    # print('!!!!!!restart!!!!!!!!')
    print('!!!!!!exit!!!!!!!!')
