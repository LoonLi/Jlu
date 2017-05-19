---
layout: post
title:  "Python技巧总结--函数篇"
date:   2017-04-10 11:49:45 +0200
categories: python
published: true
---
    我们的口号是，不再把Python写成C！

最近把《Python核心编程》这本书又捡起来看了看，觉得受益匪浅，做个总结。

### 0x00 参数

我们常常看到 `def func(*arg):` 这样的代码，但是 `*arg` 是个什么玩意理解不过来。Python里函数的参数也是有很多名堂的。

<br/>

Python的函数参数分为 **位置参数** 和 **默认参数** 。默认参数即C的缺省参数。默认参数必须放在位置参数的后方，否则的话会报错。

```python
>>> def func(arg1,arg2,agr3=1,arg4=2):
...     pass
...
>>> def func(arg1,arg2=1,agr3,arg4=2):
...     pass
...
  File "<stdin>", line 1
SyntaxError: non-default argument follows default argument
```

然后在参数前加星号，即 `*arg` 可传递参数组。作为结果就是把参数以列表形式传递。

```python
>>> def func(*arg):
...     for i in arg:
...             print i
...
>>> func(1,2,3)
1
2
3
```

如果在参数前加两个星号，即 `**arg` 可传递参数字典。

```python
>>> def func(**arg):
...     for i in arg:
...             print "[%s : %d]"%(i,arg[i])
...
>>> func(arg1=1,arg2=2,arg3=3)
[arg1 : 1]
[arg2 : 2]
[arg3 : 3]
```

我们还可以在传递参数时手动加星号指定参数是属于可变参数的部分。

```python
>>> def func(arg1,arg2,*nkw,**kw):
...     print 'arg1 is :',arg1
...     print 'arg2 is :',arg2
...     for i in nkw:
...             print 'additional non-keyword arg :',i
...     for k in kw:
...             print "addtional keyword arg '%s': '%s'"%(k,kw[k])
...
>>> func(1,2,3,4,aaa=5,bbb=6)
arg1 is : 1
arg2 is : 2
additional non-keyword arg : 3
additional non-keyword arg : 4
addtional keyword arg 'aaa': '5'
addtional keyword arg 'bbb': '6'
>>> func(1,2,3,4,aaa=5,bbb=6,*(7,8),**{'ccc':9,'ddd':10})
arg1 is : 1
arg2 is : 2
additional non-keyword arg : 3
additional non-keyword arg : 4
additional non-keyword arg : 7
additional non-keyword arg : 8
addtional keyword arg 'aaa': '5'
addtional keyword arg 'bbb': '6'
addtional keyword arg 'ccc': '9'
addtional keyword arg 'ddd': '10'
```

### 0x01 装饰器

在写flask的时候碰到过 `@route()` 的代码，当时并不明白什么意思就直接用了。

<br/>

装饰器可以通过在函数定义前增加以@开头的语句来对函数进行加工。说起来复杂，举个例子就明白了。

```python
def decorator(func):
    def warppedFunc(a,b):
        print '*%s* has been decorated!'%(func.__name__)
        return func(a,b)
    return warppedFunc

@decorator
def foo(a,b):
    print a+b

if __name__ == '__main__':
    foo(1,2)
```

代码的输出结果是

```
*foo* has been decorated!
3
```

也就是装饰器将函数名作为参数，应该返回一个新函数，新函数返回原函数的调用。当然不返回原函数的调用也没有任何语法错误，只是没有意义了。

<br/>

装饰器还可以有参数。如果加了参数那么就相当于调用 `decorote(arg)(func)` 。

```python
def decorator(arg):
    arg+=1
    print arg
    def warppedFunc(func):
        def warppedWarppedFunc(a,b):
            print '*%s* has been decorated!'%(func.__name__)
            return func(a,b)
        return warppedWarppedFunc
    return warppedFunc

@decorator(1)
def foo(a,b):
    print a+b

if __name__ == '__main__':
    foo(1,2)
```

输出结果是

```
2
*foo* has been decorated!
3
```

### 0x02 函数属性

函数下的第一行字符串将作为函数的 `__doc__` 属性。

```python
def foo():
    'Hi! I am the help doc of this function!'
    pass

if __name__ == '__main__':
    print foo.__doc__
```

输出结果

```
Hi! I am the help doc of this function!
```

### 0x03 lambda及一些内建函数

##### lambda

通过 `lambda` 关键字可以创建匿名函数。

```python
>>> a = lambda x,y:x+y
>>> a(1,2)
3
```

语法也很简单，即 `lambda arg1[,arg2,...]:<expression>` 。对于一些简单的运算函数可以简化代码。

##### filter()

一个用来过滤队列中元素的内建函数，参数是 `filter(func,seq)` 。func需要有一个参数，并且返回一个布尔值。列表中经过表达式运算结果为真的元素会被留下。

```python
>>> filter(lambda x:x%2,range(10))
[1, 3, 5, 7, 9]
```

但也可以用一个list替代它。

```python
>>> [x for x in range(10) if x%2]
[1, 3, 5, 7, 9]
```


##### map()

map()与filter()的不同点在于map()是对元素进行加工运算。

```python
>>> map(lambda x:x+2,range(10))
[2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
```

如果map()中有多个seq参数，那么每个seq会逐位增加到func的参数中。比如有两个列表，那么func的参数就有两个。

```python
>>> map(lambda x,y:x*y,[1,2,3],[4,5,6])
[4, 10, 18]
```

map()还有一种特殊用法。

```python
>>> map(None,[1,2,3],[4,5,6])
[(1, 4), (2, 5), (3, 6)]
```

这种用法后来被zip()取代了。

```python
>>> zip([1,2,3],[4,5,6])
[(1, 4), (2, 5), (3, 6)]
```

##### reduce()

简单地说，reduce()就是用来完成累加这种列表中元素逐个累运算的。因为是每两位一的运算，所以func有两个参数。

```python
def foo(seq):
    result = 0
    for x in seq:
        result+=x
    return result

if __name__ == '__main__':
    seq = range(10)
    print 'foo(seq) =',foo(seq)
    print 'reduce(lambda x,y:x+y,seq) =',reduce(lambda x,y:x+y,seq)
```

输出结果是

```python
foo(seq) = 45
reduce(lambda x,y:x+y,seq) = 45
```

### 0x04 偏函数

偏函数可以在给函数添加默认参数后重命名函数，对于一些需要输入很多参数，但是每次只要改变一个参数的函数，能起到简化代码的效果。

```python
from functools import partial

def foo(arg1,arg2,arg3):
    return (arg1*arg3)+arg2

if __name__ == '__main__':
    newFoo = partial(foo,arg1=2,arg3=5)
    print newFoo(arg2=5)
```

结果是 `15`

需要注意的是输入参数的顺序，如果参数顺序错了是会报错的。

### 0x05 变量作用域

##### global

有时我们想在函数中使用全局变量，使用global声明一下就行。

```python
global I_am_the_global_var
```

##### 闭包

使用闭包会把一些变量封装在一个流浪的作用域里。

```
def counter(start_at=0):
    count = [start_at]
    def incr():
        count[0]+=1
        return count[0]
    return incr

def foo(func):
    print 'I call the counter in foo(),the count is:',func()

if __name__ == '__main__':
    count = counter(10)
    print 'This is my first call count in main.It is:',count()
    foo(count)
    print 'This is my second call count in main.It is:',count()
```

结果是

```
This is my first call count in main.It is: 11
I call the counter in foo(),the count is: 12
This is my second call count in main.It is: 13
```

明明不是全局变量却能够在各个变量作用域被改变，非常神奇。需要注意的是变量必须是存储在队列中的。

### 0x06 生成器yield

Python可以利用yield关键字生成一个迭代器，可以使用next()方法和forin来访问。

```
>>> def gen(arg):
...     for i in range(arg):
...             yield i
...
>>> myG = gen(2)
>>> myG.next()
0
>>> myG.next()
1
>>> myG.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

当全部生成完成后，再使用next()方法会报错。另外可以使用close()方法关闭生成器。

<br/>

另外就是forin来访问。

```python
>>> myG = gen(2)
>>> for i in myG:
...     print i
...
0
1
```

### 0x07 总结

到这里总结了部分Python函数的特性，作以笔记。