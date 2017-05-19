---
layout: post
title:  "gdb修改寄存器"
date:   2017-03-26 11:49:45 +0200
categories: ctf
published: true
---
    这篇文章做个gdb修改寄存器的教程。gdb需要安装插件，详细可看https://loonli.github.io/GateofBabylon/ctf/2017/03/20/overflow.html

题目可以在这里下载[http://pan.baidu.com/s/1qYxyATY](http://pan.baidu.com/s/1qYxyATY)。

### 0x00 使用ida pro分析代码

`main()`的逻辑很简单，我们直接分析`check()`函数。

<br/>

![p1](http://ofnd3snod.bkt.clouddn.com/blog/ctf/gdbPatch/p1.png)

<br/>

首先在for循环处，判断输入是否与`flag`这个全局变量相同。（双击`flag`可以看到flag的值）如果相同会让你输入，然后经过`culc()`这个函数判断你的输入是否能通过if，如果能就输出经过`enc()`加密的flag。 。但是点进关键的`culc()`函数的话会发现一个很尴尬的情况:

<br/>

![p2](http://ofnd3snod.bkt.clouddn.com/blog/ctf/gdbPatch/p2.png)

<br/>

什么？返回0？这不是永远通不过判断了么？所以我们需要用gdb来修改内存或或寄存器。

### 0x01 gdb修改内存

关于gdb基础的文件导入和下断点在开头提到的文章有提到，这里讲的不详细的话可以去看看。

<br/>

首先我们导入文件然后查看`check()`函数，并找到if判断的位置。

<br/>

![p3](http://ofnd3snod.bkt.clouddn.com/blog/ctf/gdbPatch/p3.png)

<br/>

然后我们注意到这里调用了函数`culc()`那么接下来那个`je`就是我们要找的跳转。关于`test eax,eax`，test的原理可以自己查查，总之这里让eax不为0，那么就能不跳转。那么我们在这一行下断点：

<br/>

![p4](http://ofnd3snod.bkt.clouddn.com/blog/ctf/gdbPatch/p4.png)

<br/>

然后使用r命令让程序跑起来，输入flag对应的值`&&jj66`后，会让你输入，但随便输就行，输完之后就会停在断点。我们来查看eax的值。

<br/>

![p5](http://ofnd3snod.bkt.clouddn.com/blog/ctf/gdbPatch/p5.png)

<br/>

是0，那么我们把它改成1就行。使用`set`命令。然后再使用`c`命令让程序继续运行。

<br/>

![p6](http://ofnd3snod.bkt.clouddn.com/blog/ctf/gdbPatch/p6.png)

<br/>

成功得到了flag。

### 0x02 总结

这题最难的地方应该不是修改寄存器，而是找到需要修改的位置。需要对汇编语言有一定的理解相对应的练习。