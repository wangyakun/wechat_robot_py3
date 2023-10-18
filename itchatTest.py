# coding=utf8
__author__ = 'WYK'

import os
import traceback

import itchat
import time
from itchat.content import *


class LOG:
    def __init__(self):
        self.LOG_HOME = r'D:\log\itchatTestLog'
        self.is_record_log = True
        self.ensure_dir_exist()

        # logging.basicConfig(level=logging.DEBUG,
        #                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        #                     datefmt='%a, %d %b %Y %H:%M:%S',
        #                     filename=os.path.join(self.LOG_HOME, 'wxRobot.log'),
        #                     filemode='w')

    def ensure_dir_exist(self, suffix=None):
        new_dir = os.path.join(self.LOG_HOME, suffix) if suffix is not None else self.LOG_HOME
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        return new_dir

    def get_resource_dir(self, user='default'):
        return self.ensure_dir_exist(user)

    def log(self, message, user='default'):
        if not self.is_record_log:
            return
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        filepath = os.path.join(self.LOG_HOME, user + '.log')
        print(filepath)
        print(now)
        print(message)
        # logging.info(message)
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(now)
            f.write('\n')
            f.write(message)
            f.write('\n')

    def log_text(self, msg, isGroupChat=False):
        chatNickName = msg['User'].get('NickName')
        fromUserNickName = msg.actualNickName if isGroupChat else itchat.search_friends(userName=msg['FromUserName']).get('NickName')
        logName = '(群聊)' + chatNickName if isGroupChat else chatNickName
        logger.log('【%s】' % msg.type + fromUserNickName + ':' + msg['Text'], logName)

    def log_media(self, msg, isGroupChat=False):
        chatNickName = msg['User'].get('NickName')
        fromUserNickName = msg.actualNickName if isGroupChat else itchat.search_friends(userName=msg['FromUserName']).get('NickName')
        logName = '(群聊)' + chatNickName if isGroupChat else chatNickName
        download_path = os.path.join(logger.get_resource_dir(logName), msg.fileName)
        msg.download(download_path)
        logger.log(fromUserNickName + ':【接收到 %s 类型文件，已保存在 %s 】' % (msg.type, download_path), logName)

logger = LOG()

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    # print(msg)
    # msg.user.send('%s: %s' % (msg.type, msg.text))
    logger.log_text(msg)

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    # print(msg)
    # msg.download(msg.fileName)
    # typeSymbol = {
    #     PICTURE: 'img',
    #     VIDEO: 'vid', }.get(msg.type, 'fil')
    # return '@%s@%s' % (typeSymbol, msg.fileName)
    logger.log_media(msg)

# @itchat.msg_register(FRIENDS)
# def add_friend(msg):
#     msg.user.verify()
#     msg.user.send('Nice to meet you!')

# first = True

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    # global first
    # if first:
    #     print(msg)
    #     first = False
    # if msg.isAt:
    #     msg.user.send(u'@%s\u2005I received: %s' % (
    #         msg.actualNickName, msg.text))

    logger.log_text(msg, True)

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def download_files(msg):
    logger.log_media(msg, True)

if __name__ == '__main__':
    try:
        itchat.auto_login(True)
        itchat.run(True)
        print('end!!!!!')
    except Exception as e:
        print(traceback.format_exc())
        time.sleep(5)
