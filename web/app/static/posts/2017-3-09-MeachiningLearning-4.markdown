---
layout: post
title:  "python机器学习笔记（4）—— Logistic回归"
date:   2017-03-09 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是Logistic回归？

Logistic回归是一个二分类算法。首先我们要找到一个函数f(x)，当x足够小时f(x)等于0，当x足够大时f(x)等于1，且存在一个阶跃点x，使f(x)能瞬间从0跳跃到1。对此 **Sigmoid函数**是符合要求的。它的公式是![公式](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/Logistic/sigmoid_function.gif)，图如下图：


![graph](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/Logistic/sigmoid.png)


我们假定Sigmoid函数的输入是z，设z=w0x0+w1x1+...+wNxN，其中xN对应实体的每个特征。我们需要做的工作就是找到合适的权重W，使我们的输入能够拟合到Sigmoid函数上，对于函数结果大于0.5值的实体分类为1，对于函数结果小于0.5的结果分类为0。


然后再引入一个概念是 **梯度上升算法**。它的作用是使我们的权重W（向量）逐步逼近最大值，也就是最佳值。


有了以上这些基础，便可以开始编写代码了。

- **优点：**计算代价较低，易于实现。
- **缺点：**容易欠拟合，分类精度不高。
- **适用数据范围：**数值型和标量型。

### 0x01 批量计算法

首先我们使用的是批量计算的方式，即每次计算都会把所有的数据样本用到。

```python
def sigmoid(inX):
    return 1.0/(1+exp(-inX))

def gradAscent(dataMatIn, classLabels):
    dataMatrix = mat(dataMatIn)             
    labelMat = mat(classLabels).transpose() 
    m,n = shape(dataMatrix)
    #alpha是梯度上升中每次逼近的步数
    alpha = 0.001
    maxCycles = 500
    weights = ones((n,1))
    for k in range(maxCycles):
        #值得注意的是h与error都是向量              
        h = sigmoid(dataMatrix*weights)
        #error是每个标签的真实值与计算结果的差值    
        error = (labelMat - h) 
        #下面这一步就是梯度上升算法             
        weights = weights + alpha * dataMatrix.transpose()* error 
    return weights
```

### 0x02 画出决策边界

我们用100个样本，每个样本两个特征的数据来做测试。

```python
def loadDataSet():
    dataMat = []; labelMat = []
    fr = open('testSet.txt')
    for line in fr.readlines():
        lineArr = line.strip().split()
        #为了方便画图，增加了一个全为1.0的特征
        dataMat.append([1.0, float(lineArr[0]), float(lineArr[1])])
        labelMat.append(int(lineArr[2]))
    return dataMat,labelMat

#weights是0x01中函数的输出结果
def plotBestFit(weights):
    import matplotlib.pyplot as plt
    dataMat,labelMat=loadDataSet()
    dataArr = array(dataMat)
    n = shape(dataArr)[0] 
    xcord1 = []; ycord1 = []
    xcord2 = []; ycord2 = []
    for i in range(n):
        if int(labelMat[i])== 1:
            xcord1.append(dataArr[i,1]); ycord1.append(dataArr[i,2])
        else:
            xcord2.append(dataArr[i,1]); ycord2.append(dataArr[i,2])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xcord1, ycord1, s=30, c='red', marker='s')
    ax.scatter(xcord2, ycord2, s=30, c='green')
    x = arange(-3.0, 3.0, 0.1)
    y = (-weights[0,0]-weights[1,0]*x)/weights[2,0]
    ax.plot(x, y)
    plt.xlabel('X1'); plt.ylabel('X2');
    plt.show()
```

对于y的赋值，是由这样一条式子得到的: 0 = w0*1.0 + w1*x + w2*y。对于这个1.0，上面的注释也提到了。有了这个1.0，就可以画出容易分析的二维图像。图如下所示：

![graph](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/Logistic/logistic.png)

### 0x03 随机计算法

上面的批量方法虽然匹配效果好，但是计算量较大，不够实用。所以可以采用一种随机选择样本的方式来减少计算次数。

```python
def stocGradAscent1(dataMatrix, classLabels, numIter=150):
    m,n = shape(dataMatrix)
    weights = ones(n)   
    for j in range(numIter):
        dataIndex = range(m)
        for i in range(m):
            #这种alpha的设定方式能够使j在足够大时，新的样本同样能对权重的值做出贡献。即后面的数据也能有意义。
            alpha = 4/(1.0+j+i)+0.0001    
            #随机选择样本 
            randIndex = int(random.uniform(0,len(dataIndex)))
            h = sigmoid(sum(dataMatrix[randIndex]*weights))
            error = classLabels[randIndex] - h
            weights = weights + alpha * error * dataMatrix[randIndex]
            del(dataIndex[randIndex])
    return weights
```
