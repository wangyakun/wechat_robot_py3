# wechat_robot

## 微信自动回复机器人

使用方法：

1.python selfWechatRobot.py

2.微信扫二维码登录

原理：

1.使用itchat微信接口，可获取聊天内容及发送微信消息

2.将获取到的聊天内容对接到青云客机器人(api.qingyunke.com)，得到回复，发送回去

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

“auther” 作者信息

## 微信自动回复机器人-后台（暂未实现）

使用方法：

0.(os.system里面是本人树莓派目录，不同环境请自行改动)

1.python wechatRobot_bakend.py

2.微信扫二维码登录

控制台操作：
向 文件传输助手 发送：

“new” 新登录-微信自动回复机器人

“auther” 作者信息