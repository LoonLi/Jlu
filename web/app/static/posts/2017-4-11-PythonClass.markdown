---
layout: post
title:  "Python技巧总结--类篇"
date:   2017-04-11 11:49:45 +0200
categories: python
published: true
---
    我们的口号是，不再把Python写成C！

最近把《Python核心编程》这本书又捡起来看了看，觉得受益匪浅，做个总结。

### 0x00 类的属性

##### \_\_doc\_\_

这个与函数的一样，类下的一行字符串。

```python
class myClass(object):
    'Hi! I am the __doc__!'
    pass

if __name__ == '__main__':
    print myClass.__doc__

#Hi! I am the __doc__!
```

##### \_\_dict\_\_

它能得到得到类内变量。

```
class myClass(object):
    'Hi! I am the __doc__!'
    a = 1
    b = 'bbb'
    def foo():pass

if __name__ == '__main__':
    print myClass.__dict__


#{'a': 1, '__module__': '__main__', 'b': 'bbb', '__dict__': <attribute '__dict__' of 'myClass' objects>, 'foo': <function foo at 0x02A888B0>, '__weakref__': <attribute '__weakref__' of 'myClass' objects>, '__doc__': 'Hi! I am the __doc__!'}
```

### 0x01 \_\_new\_\_()与 \_\_init\_\_()

类在实例化时会先调用\_\_new\_\_()，并返回一个类对象，然后再调用\_\_init\_\_()对类进行初始化操作。我们可以通过改变new内的代码来让类返回一个完全不同的值。new()有一个默认参数 `cls` ，它其实就是原本应该返回的类实例对象。

```python
class myClass(object):
    def __new__(cls):
        return [1,2,3]

if __name__ == '__main__':
    c = myClass()
    print c

#[1, 2, 3]
```

### 0x02 \_\_str\_\_()与 \_\_repr\_\_()

覆盖类中的这两个方法能够改变类的被输出类型。

```python
class myClass(object):
    def __str__(self):
        return 'Hello!'
    __repr__ = __str__

if __name__ == '__main__':
    c = myClass()
    print c
    print repr(c)
#Hello!
#Hello!

```

使用 `__repr__ = __str__` 的形式，当 `__str__` 中代码出现bug时能方便修改。

### 0x03 运算符重载

python还准备了一些函数用来重载类的运算符。

```python
class myClass(object):
    def __init__(self,a):
        self.a = a

    def __add__(self,other):
        return self.a + other.a

if __name__ == '__main__':
    c = myClass(1)
    cc = myClass(2)
    print c+cc #3
```

除了 `__add__` ，各种运算符都有对应的函数。

### 0x04 \_\_iter()\_\_与next()

覆盖\_\_iter()\_\_以及next()能够实现自定义迭代器的功能。函数在被迭代时，首先调用 `__iter__()` ，返回自己的迭代对象，然后再调用迭代对象的next()方法。所以我们有两种实现方法。

<br/>

第一种是让 `__iter()__` 直接返回一个可迭代对象，即带有 `next()` 方法的对象。

```python
class myClass(object):
    def __init__(self,a):
        self.a = iter(a)

    def __iter__(self):
        return self.a



if __name__ == '__main__':
    c = myClass(range(3))
    for i in c:
        print i

# 0
# 1
# 2
```

另一种是返回一个添加了 `next()`方法的类。

```python
class myClass(object):
    def __init__(self,a):
        self.a = iter(a)

    def __iter__(self):
        return self

    def next(self):
        return self.a.next()


if __name__ == '__main__':
    c = myClass(range(3))
    for i in c:
        print i

# 0
# 1
# 2
```

### 0x05 包装

我们可以通过包装一个类来改变或者增强其功能。原理是 `getattr(obj,attr)` 能够返回对象的属性，比如：

```python
class myClass(object):
    def __init__(self,a):
        self.a = a

    def foo():pass


if __name__ == '__main__':
    c = myClass(10)
    print getattr(c,'a')
    print getattr(c,'foo')

# 10
# <bound method myClass.foo of <__main__.myClass object at 0x02C04130>>
```

那么我们只要改写一下 `__getattr__()` 方法，就能实现包装功能。

```python
class myClass(object):
    def __init__(self,a):
        self.a = a

    def __getattr__(self,attr):
        return getattr(self.a,attr)

    def __str__(self):
        return str(self.a)

    __repr__ = __str__


if __name__ == '__main__':
    c = myClass(range(3))
    print c
    c.append(3)
    print c
    print c.pop()

# [0, 1, 2]
# [0, 1, 2, 3]
# 3
```

`myClass`类成功调用了自己没有定义的方法，因为通过 `getattr()` 得到了 `self.a` 的方法。

### 0x06 \_\_getitem()\_\_

当出现 `obj[i]` 时，实际上被调用的就是obj中的__getitem()__方法。所以改变这个方法就能利用 `[]` 来获取别的内容啦。

```python
class myClass(object):
    def __init__(self,a):
        self.a = a

    def __getitem__(self,i):
        return self.__dict__.get(i,None)


if __name__ == '__main__':
    c = myClass('I am a!')
    print c['a']
    print c['b']

# I am a!
# None
```

### 0x07 总结

到此总结一些可能用得上的Python技巧，以笔记。

