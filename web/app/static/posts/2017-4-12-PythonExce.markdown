---
layout: post
title:  "Python技巧总结--执行篇"
date:   2017-04-12 11:49:45 +0200
categories: python
published: true
---
    我们的口号是，不再把Python写成C！

最近把《Python核心编程》这本书又捡起来看了看，觉得受益匪浅，做个总结。

### 0x00 eval()

eval()相当于在Python交互环境下输入语句。比方说：

```python
>>> [1,2,3]
[1, 2, 3]
```

以上是在交互环境下得到的结果，那么：

```python
if __name__ == '__main__':
    a = eval('[1,2,3]')
    print type(a)
    print a

# <type 'list'>
# [1, 2, 3]
```

### 0x01 exec关键字

exec()能够执行作为参数的字符串或是代码对象。而代码对象是由compile()函数返回的。

```python
if __name__ == '__main__':
    code = compile("print 'I am code!'",'','exec')
    exec code
    exec "print 'I am another code!'"

# I am code!
# I am another code!
```

执行代码对象的效率会更高。

### 0x02 input()

input()会把输入的字符串作为参数传入eval()函数，返回eval()的结果。而raw_input()则是获得原本的字符串。

```python
if __name__ == '__main__':
    result = input()
    string = raw_input()
    print result
    print string

# < 100+50
# < 100+50
# 150
# 100+50
```

### 0x03 os.system()

这个函数可以执行命令行命令。

```python
import os

if __name__ == '__main__':
    os.system('dir C:\Users\Administrator\Desktop')

#  驱动器 C 中的卷没有标签。
#  卷的序列号是 1C04-7581

#  C:\Users\Administrator\Desktop 的目录

# 2017/04/12  16:36    <DIR>          .
# 2017/04/12  16:36    <DIR>          ..
# 2017/04/12  16:47               133 t.py
#                1 个文件            133 字节
#                2 个目录 34,200,911,872 可用字节
```

### 0x04 总结

这里内容不是很多。