---
layout: post
title:  "PWN之基础栈溢出"
date:   2017-03-20 11:49:45 +0200
categories: ctf
published: true
---
    这里对一道非常简单的pwn（甚至可以说最简单）做一个讲解。

题目可以在这里下载[http://pan.baidu.com/s/1mhKqOjQ](http://pan.baidu.com/s/1mhKqOjQ)。

### 0x00 使用ida pro分析代码

对于PWN题，有的题目是不会给你程序的，但有的会给，比如这个题目。拿到题目之后，首先使用IDA PRO分析代码。对于IDA PRO可以使用我这个[http://pan.baidu.com/s/1o7IkRBO](http://pan.baidu.com/s/1o7IkRBO)。

<br/>

IDA PRO打开它的文件夹后可以看到它有两个版本，一个对应32位程序，一个对应64位程序。对于32位和64位程序的区别这里就不做详细叙述，直接讲IDA的使用方法。

<br/>

因为这道题的题目是64位的（如果使用了错误版本的IDA，IDA会给你提示），所以我们用64位的IDA打开它，然后可以看到IDA的代码分析结果。

<br/>

这里是函数界面。双击里面的函数在反汇编界面看到该函数的反汇编结果。

![p1](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/01.png)

<br/>

这里是IDA的反汇编界面。在这个界面按 `空格`可以切换到其他的现实模式。

![p2](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/02.png)

<br/>

比如可以按空格切换到main函数的这个界面。这个界面里的代码是汇编代码，想要读懂的话需要学习相关知识。

![p3](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/03.png)

<br/>

这里我们用到的就这么多，所以先介绍到这里。那么有同学会问了，汇编太难了，我读不懂该怎么办？这里就能用到IDA PRO最强大的功能之一————反汇编到C语言代码。还是在刚刚main函数的位置，我们按下`F5`，然后可以看到main函数的反汇编到C语言的代码。

![p4](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/04.png)

<br/>

这下分析代码就变得轻松多了。因为这个程序的函数也不是很多，我们可以逐个看看这些函数哪个比较可疑，然后我们注意到了一个名字叫 **good_game**的函数，里面有一句代码是 `v0 = fopen("flag.txt", "r");`。这个 **flag.txt**实在是相当可疑。可是这个程序 **main**函数里只是读取了我们的输入呀，怎么才能让它进入这个函数呢？

<br/>

这里就涉及到了栈溢出的知识。

### 0x01 栈溢出

栈溢出是PWN中最常利用的漏洞之一，它涉及到了程序运行中 **栈帧**的概念。那么什么是栈帧呢？对于栈溢出知识的介绍网上有很多人介绍过，这篇博客主要教大家一些PWN工具的利用，所以这里就给出几个链接，大家可以通过这几个链接学习栈溢出的知识。

<br/>

[以动画的形式生动演示了栈溢出的过程](https://www.codebashing.com/io/lessons/stack_overflow/#/lesson/stack overflows/objectives?_k=608z53)

[知乎上的一些回答](https://www.zhihu.com/question/22444939)

[这篇对寄存器指针的说明比较详细](http://eleveneat.com/2015/07/11/Stack-Frame/)

<br/>

应用到我们这个程序中来，大概是这样一个分析过程。首先我们观察这个 **read()**函数。

`read(0, &v4, 0x100uLL);`

可以看出来它是往 `v4`这个变量储存的地址里，读取 **0x100**个字符的输入（ **0x**前缀表示这是个16进制数），那么我们关注一下 `v4`在栈中的位置。

<br/>

`__int64 v4; // [sp+0h] [bp-88h]@1`

可以看出来，它在 **bp-88h**这个位置。**88h**中的 **h**表明这是个16进制数。根据我们栈帧的知识， **bp**中存储的是函数的返回地址，如果我们能利用我们的输入把bp对应的地址给覆盖成 **good_ganme**对应的地址，那么程序在走完 **main()**之后，将会返回到 **good_game()**，运行读取flag的代码。

<br/>

想必对于初学者来说理解这些是比较困难的，但万事开头难，想要深入的话这样的学习是必要的，如果自己想要学习的话，我推荐去看看汇编语言相关的书籍，能对程序的运行有更深入的理解。


## 0x02 gdb动态调试

上面分析了一堆，到底能不能在实践上用上呢？我们可以通过 **gdb**工具来动态调试linux下可执行文件。在运行 **gdb**之前，我推荐大家安装一个插件，地址在[这里](https://github.com/longld/peda)。如果看不懂readme的意思的话，在linux的命令行中执行以下两行代码：

```shell
git clone https://github.com/longld/peda.git ~/peda
echo "source ~/peda/peda.py" >> ~/.gdbinit
```

即可安装上这个gdb插件。让我们看看实际的操作。

<br/>

首先在目标文件目录下使用gdb命令。

![p5](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/05.png)

<br/>

然后输入`file [文件名]`，让gdb导入该文件。（注意要是不在被导入文件的目录下是不能导入文件的）

![p6](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/06.png)

<br/>

然后输入`disas main`即“反编译main函数”的意思。

![p7](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/07.png)

<br/>

然后使用`b *(main+42)`在read()函数后加断点。加了断点之后程序在运行时就会停在断点处。

![p8](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/08.png)

<br/>

使用`r`让程序跑起来。然后随便输入一段字符。

![p9](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/09.png)

<br/>

上图的中间有许多调试信息，这里我们关注一下 **RBP**的信息，然后输入`stack 50`查看栈的50行信息。

![p10](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/10.png)

我们成功看到了我们的输入，和在 **0096**这个位置的 **RBP**对应的数值。感兴趣的同学可以在这里手动输入0x88个以上的字符实验一下结果。动态调试证明了我们的结论，那么让我们开始写解题脚本吧！

    gdb是个非常强大的调试工具，这里只用到了它的极少部分功能，有兴趣的同学可以自行查询资料。

### 0x03 编写脚本

PWN题通常使用python来写脚本的，当然也有用C来写脚本的大神，我们这里就用python中的`pwn`包来完成脚本的任务。

    安装pwn包非常简单。在命令行中输入pip install pwn即可。

<br/>

直接把脚本放上来:

```python
#!/usr/bin/env python
#-*- coding:utf-8 -*-
 
from pwn import *
 
conn = remote('45.32.93.239', 54321)
print conn.recvline()
payload = "a" * 0x88          
payload += p64(0x0000000000400620)  #这串数字是good_game的函数地址
conn.sendline(payload)
print conn.recv()
print conn.recv()
```

对代码作部分说明。 `remote()`是链接到题目服务器的函数。 `recvline()`是接收服务器传来的一行字符。`payload`是我们要提交的字符串。`p64()`是把16进制数字转化成64位地址字符串的函数。`sendline()`是发送一行数据到服务器。`recv()`是接收服务器的数据。

<br/>

代码还是相当直观的，应该比较好理解。可能有同学不知道good_name函数地址是如何获取的。我们可以通过ida来获取。首先把反汇编界面调到带地址的汇编代码，然后在函数窗口双击good_game函数即可。

<br/>

首先要切到这个栏，然后按空格可以切到带地址的状态。

![p11](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/11.png)

<br/>

然后双击good_game函数地址就能看到了。

![p12](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/12.png)

<br/>

最后展示以下脚本运行的结果。

![p13](http://ofnd3snod.bkt.clouddn.com/blog/ctf/overflow/13.png)