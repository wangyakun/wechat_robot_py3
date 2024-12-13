#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'WYK'

import re

import subprocess

import shutil

import itchat
import traceback
import time
import os

robot_instance_num = -1

help_info = '''“new” 新登录-微信自动回复机器人
“del xxx” 删除第xxx个微信自动回复机器人
“list” 查看自动回复机器人列表
“auther” 作者信息'''
curr_dir = os.path.dirname(os.path.realpath(__file__))
backend_dir = os.path.join(curr_dir, 'robot_from_backend')
processes = {}

def ctl_msg(msg):
    global help_info, robot_instance_num
    if msg['ToUserName'] != 'filehelper':
        return False
    print('!!!this is admin!!!')
    print('msg:')
    print(msg['Text'])

    if msg['Text'] == 'new':
        robot_instance_num += 1
        itchat.send(f'新登录,子进程号：{robot_instance_num}', 'filehelper')
        curr_process_dir = os.path.join(backend_dir, str(robot_instance_num))
        curr_process_logs_dir = os.path.join(curr_process_dir, 'logs')
        curr_process_qr_path = os.path.join(curr_process_dir, 'QR.png')
        curr_process_output_path = os.path.join(curr_process_dir, 'output_and_errors.txt')
        os.makedirs(curr_process_dir)
        os.makedirs(curr_process_logs_dir)
        cmd_list = ['python', os.path.join(curr_dir, 'selfWechatRobot.py'), f'--qrcode_dir={curr_process_qr_path}',
                    f'--log_home={curr_process_logs_dir}', '--no_hot_reload']
        print(f'cmd:{" ".join(cmd_list)}')
        with open(curr_process_output_path, 'w') as outfile:
            process = subprocess.Popen(cmd_list, stdout=outfile, stderr=subprocess.STDOUT)
            processes[f'{robot_instance_num}'] = process
        for i in range(5):
            if os.path.exists(curr_process_qr_path):
                break
            itchat.send(u'请稍等...%d' % i, 'filehelper')
            time.sleep(1)
        itchat.send_image(curr_process_qr_path, 'filehelper')
    elif match := re.match(r'^del (\d+)$', msg['Text']):
        if process := processes.get(match.group(1)):
            process.terminate()
            itchat.send(f'关闭{match.group(1)}成功', 'filehelper')
        else:
            itchat.send(f'关闭{match.group(1)}失败', 'filehelper')
    elif msg['Text'] == 'list':
        itchat.send(f'list:{processes}', 'filehelper')
    elif msg['Text'] == 'auther':
        itchat.send(u'wechat-robot auther:君莫思归', 'filehelper')
    elif msg['Text'] == 'help':
        itchat.send(help_info, 'filehelper')
    return True


@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    if ctl_msg(msg):
        return


def main():
    # itchat.auto_login(hotReload=True, enableCmdQR=True)
    itchat.auto_login(hotReload=True, enableCmdQR=False)
    itchat.run()


if __name__ == '__main__':
    print('!!!!!!start wechatRobot_bakend!!!!!!!!')
    if os.path.exists(backend_dir):
        shutil.rmtree(backend_dir)
    os.makedirs(backend_dir)

    main()
    print('!!!!!!exit wechatRobot_bakend!!!!!!!!')
'''
    while True:
        try:
            main()
            print('end!!!!!')
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            time.sleep(5)
        print('!!!!!!restart!!!!!!!!')
        '''
