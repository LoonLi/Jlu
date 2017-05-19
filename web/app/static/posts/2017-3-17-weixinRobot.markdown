---
layout: post
title:  "微信机器人部署"
date:   2017-03-17 11:49:45 +0200
categories: tech
published: true
---
    看到别人搞了个telegram的自动发图机器人，眼馋也自己搞了个微信机器人玩。

首先使用的开源程序地址在[这里](https://github.com/liuwons/wxBot)。readme里用法写的非常详细这里就不赘述了。

<br/>

然后把图片传到服务器里，写好代码脚本。

```python
#!/usr/bin/env python
# coding: utf-8
#

from wxbot import *

from os import listdir
from os.path import isfile, join
import random

def getImg(dir_path):
    mypath = dir_path
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    fname = onlyfiles[random.randint(0, len(onlyfiles)-1)]
    return dir_path+fname

class MyWXBot(WXBot):
    def handle_msg_all(self, msg):
        if  msg['content']['type']==0:
            if msg['content']['data'] == 'thanksPPP':
                path = '/srv/ftp/ipad/'
                self.send_img_msg_by_uid(getImg(path),msg['user']['id'])

def main():
    bot = MyWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'tty'
    bot.is_big_contact = False 
    bot.run()


if __name__ == '__main__':
    main()
```

其中`getImg()`是返回目录下随机一个图片的路径。然后部署上服务器就好……应该是这样的，结果出现了问题。

<br/>

原来由于ssh链接时有个session的限制，如果在ssh下想要在服务器后台运行Py脚本，光靠`python filename.py &`是不够的，因为在关闭了ssh链接后你的后台进程也会被关闭。这时有两种解决方法。一是使用`nohup`命令，在原命令前加一个`nohup`就解决了。二是使用screen命令，在不加&的情况下进入py程序，然后按`ctrl+a`再按`d`就可以进入暂停界面。详细在这篇[文章](https://github.com/gatieme/AderXCoding/tree/master/system/tools/ssh_exit)。

以下是运行效果：

![p](http://ofnd3snod.bkt.clouddn.com/blog/tech/wechatRobot/S70317-11485926.jpg)

效果还是不错的，日后可以增加各种功能。