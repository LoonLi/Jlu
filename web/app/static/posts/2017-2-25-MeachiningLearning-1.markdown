---
layout: post
title:  "python机器学习笔记（1）—— k邻近算法"
date:   2017-02-25 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是k邻近算法？

k邻近算法是一种通过测量与不同特征值的距离的方法进行分类的分类算法。

- **优点：**精度高，对异常值不敏感，无数据输入假定。
- **缺点：**算法的时间，空间复杂度很高，实用性不强。
- **适用数据范围：**数值型，标量型。

使用k邻近算法需要有一个样本数据集合，也称为训练样本集，并且样本集中每个数据都存在标签，即我们知道样本的每一个数据的分类。在输入没有标签的数据后，将数据与样本进行距离计算，距离短的数据中出现频率最高的类别即可认为是该数据的标签。

### 0x01 创建数据集

在涉及到矩阵运算的算法中，可以使用python的`numpy`包。

```python
#coding=UTF-8
from numpy import *
import operator

def createDataset():
    #使用array可以构建数组(线性代数)
    group = array([[1.0,1.1],[1.0,1.0],[0,0],[0,1.0]])
    labels = ['A','A','B','B']
    return group,labels
```

`array()`是`numpy`中的函数，作用是生成矩阵。其中每个元组表示行，比如上面代码中生成的矩阵就是4行2列的。

### 0x02 kNN分类算法的实现

k邻近算法按照以下思路进行编写：

- 1.计算以知类别数据中集中的点与当前点之间的距离；
- 2.按照距离递增次序排序；
- 3.选取与当前点距离最小的k个点；
- 4.确定前k个点所在类别的出现频率；
- 5.返回前k个点出现频率最高的类别作为当前点的预测分类。

```python
#输入内容分别是需要分类的向量，训练样本的数据集，数据集的对应分类，选择最近邻居的数目，返回预测分类类别
def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]
    #tile()是将向量inX在列方向上重复dataSetSize次，在行上重复1次
    diffMat = tile(inX, (dataSetSize,1)) - dataSet
    sqDiffMat = diffMat**2
    #axis这个参数看得不是很明白，官网上的解释是
    #axis : None or int or tuple of ints, optional
    #       Axis or axes along which a sum is performed. The default, axis=None, will sum all of the elements of the input array. If axis is negative it counts from the last to the first axis.
    #实例上来讲axis=1的情况计算每个向量内的和，并返回一个数组
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances**0.5
    #argsort()返回数组从小到大的索引值数组
    sortedDistIndicies = distances.argsort()
    classCount={}
    for i in range(k):
        voteIlabel = labels[sortedDistIndicies[i]]
        #dict.get()返回指定的值，如果该值不存在则返回default值
        classCount[voteIlabel] = classCount.get(voteIlabel,0) + 1
    #operator.itemgetter(n)等价于lambda x:x[n]
    #使用dir.iteritems()获得一个迭代器，然后可以获得完整的字典，否则只有目标的键值。原理尚不明确……
    sortedClassCount = sorted(classCount.iteritems(),key=operator.itemgetter(1),reverse=True)
    return sortedClassCount[0][0]
```

对于输入必须保证的是列数（即需要的数据信息）与样本相同。

距离公式使用的是欧几里得公式，即： `d = ((xA0-xB0)**2+(xA1-xB1)**2)**0.5`

### 0x03 使用Matplotlib创建散点图

python中有`matplotlib`包可以实现画图功能，它的语法与matlab相似。比如对于如下的数据：

```
[[  4.09200000e+04   8.32697600e+00   9.53952000e-01]
 [  1.44880000e+04   7.15346900e+00   1.67390400e+00]
 [  2.60520000e+04   1.44187100e+00   8.05124000e-01]
 ...,
 [  2.65750000e+04   1.06501020e+01   8.66627000e-01]
 [  4.81110000e+04   9.13452800e+00   7.28045000e-01]
 [  4.37570000e+04   7.88260100e+00   1.33244600e+00]]
```

配合该数据的标签，可以画出一个散点图。

```python
#coding=UTF-8
import kNN
import matplotlib
import matplotlib.pyplot as plt
from numpy import *

datingDataMat,datingLabels = kNN.file2matrix('datingTestSet2.txt')
print datingDataMat
print datingLabels

fig = plt.figure()
#等价于fig.add_subplot(1,1,1)
ax = fig.add_subplot(111)
#ax.scatter(x,y,s=scale,c=color)
ax.scatter(datingDataMat[:,1],datingDataMat[:,2],15.0*array(datingLabels),15.0*array(datingLabels))
plt.show()
```

对于matplotlib的散点图画法参考自[这个网站](http://note4code.com/2015/03/30/%E4%BD%BF%E7%94%A8matplotlib%E7%BB%98%E5%88%B6%E6%95%A3%E7%82%B9%E5%9B%BE/)。效果如下所示：

![图片](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/QQ%E5%9B%BE%E7%89%8720170225213644.png)

### 0x04 归一化数据

对于某些数据来说，某种属性的数据数字差值特别大，于是利用上面的公式来计算的话，该属性的值会对结果造成很大的影响。这并不是我们期望的结果，每种属性的重要性应该是相同的。比如这样两组数据，`[1,86,3,900]`，`[3,79,4,1000]`，最后的那组数据的差值相对其他属性的差值会很大。为了解决这种矛盾，可以使用以下这个公式将数值转化成`[0,1]`区间的数。

    newValue = (oldValue-min)/(max-min)

下面是代码：

```python
#归一化特征值，将数据集的数据转化成[0,1]区间的值，避免某些相对数字差值大的数据对结果影响过大
#参考公式 newValue = (oldValue - min)/(max - min)
def autoNorm(dataSet):
    #通过增加参数0使函数在数据集的列中寻找最值
    minVals = dataSet.min(0)
    maxVals = dataSet.max(0)
    ranges = maxVals - minVals
    #zero()创建一个零矩阵，shape()返回矩阵的规模
    normDataSet = zeros(shape(dataSet))
    m = dataSet.shape[0]
    normDataSet = dataSet - tile(minVals,(m,1))
    normDataSet = normDataSet/tile(ranges,(m,1))
    return normDataSet, ranges, minVals
```
