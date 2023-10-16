# wechat_robot

微信自动回复机器人


使用方法：

1.python selfWechatRobot.py

2.微信扫二维码登录

原理：

1.使用itchat微信接口，可获取聊天内容及发送微信消息

2.将获取到的聊天内容对接到图灵机器人(www.tuling123.com
)，得到回复，发送回去


功能：
1.实现了控制台，可控制如下：

  (1)打开/关闭机器人
  
  (2)对特定好友打开/关闭机器人
  
  (3)打开/关闭延时回复
  
  (4)打开/关闭打扰模式
  
控制台操作：
向 文件传输助手 发送：

“delay close” 关闭延时回复

“delay open” 打开延时回复

“disturb close” 关闭打扰模式

“disturb open” 打开打扰模式

“close” 关闭机器人

“open” 打开机器人

“close XXX” 针对XXX屏蔽自动回复

“open XXX” 针对XXX打开自动回复

“list” 查看屏蔽列表

“closelist XXX,XXX,XXX” 对多人屏蔽自动回复

“auther” 作者信息



微信自动回复机器人-后台


使用方法：

0.(os.system里面是本人树莓派目录，不同环境请自行改动)

1.python wechatRobot_bakend.py

2.微信扫二维码登录

控制台操作：
向 文件传输助手 发送：

“new” 新登录-微信自动回复机器人

“auther” 作者信息