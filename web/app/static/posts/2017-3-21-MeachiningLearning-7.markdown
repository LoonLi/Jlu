---
layout: post
title:  "python机器学习笔记（7）—— 线性回归"
date:   2017-03-21 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是线性回归？

线性回归方程其实就是满足下面式子格式的方程：

<br/>

![p0](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/00.gif)

<br/>

所以关键就是根据训练数据得到权重值 **w**。如果将平方误差写成下式：

<br/>

![p1](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/01.gif)

<br/>

那么对w求导，令式子等于0，可以得到w的表示为：

<br/>

![p2](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/02.gif)

<br/>

加帽表示最佳估计。

- **优点：**结果易于理解，计算上不复杂。
- **缺点：**对非线性的数据拟合不好。
- **适用数据范围：**数值型和标量型。

### 0x01 标准回归函数代码

```python
def standRegres(xArr,yArr):
    xMat = mat(xArr); yMat = mat(yArr).T
    xTx = xMat.T*xMat
    if linalg.det(xTx) == 0.0: #计算矩阵行列式
        print "This matrix is singular, cannot do inverse"
        return
    ws = xTx.I * (xMat.T*yMat)
    return ws
```

代码很简单，需要关注的就是在计算权重前判断了矩阵行列式是否为0.

以下两张图分别是训练数据和拟合结果。

<br/>

![p3](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/03.png)

<br/>

![p4](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/04.png)

### 0x03 局部加权线性回归

线性回归的一个问题是可能出现欠拟合现象，如上图就是。那么我们可以考虑在计算中引入一些偏差来降低预测的均方误差。其中一个方法就是局部加权线性回归，给出的回归系数计算公式如下：

<br/>

![p5](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/05.gif)

<br/>

其中 **w**是个矩阵，用来给每个数据点赋予权重。该矩阵常用核函数计算得出：

<br/>

![p6](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/06.gif)

<br/>

x距离x(i)越近，w(i,i)将会越大。而对于k，k越小，距离x(i)越远的点对权重的贡献就越小。也就是说，如果k太大，那就可能欠拟合；如果k太小，那就可能过拟合。

```python
def lwlr(testPoint,xArr,yArr,k=1.0):
    xMat = mat(xArr); yMat = mat(yArr).T
    m = shape(xMat)[0]
    weights = mat(eye((m)))
    for j in range(m):                      #next 2 lines create weights matrix
        diffMat = testPoint - xMat[j,:]     #
        weights[j,j] = exp(diffMat*diffMat.T/(-2.0*k**2))
    xTx = xMat.T * (weights * xMat)
    if linalg.det(xTx) == 0.0:
        print "This matrix is singular, cannot do inverse"
        return
    ws = xTx.I * (xMat.T * (weights * yMat))
    return testPoint * ws

def lwlrTest(testArr,xArr,yArr,k=1.0):  #loops over all the data points and applies lwlr to each one
    m = shape(testArr)[0]
    yHat = zeros(m)
    for i in range(m):
        yHat[i] = lwlr(testArr[i],xArr,yArr,k)
    return yHat
```

### 0x04 岭回归

岭回归能够解决特征数多于样本数的问题，以及帮助判断哪些特征值是有效特征值。在岭回归下，回归系数的计算公式变为：

<br/>

![p7](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/07.gif)

<br/>

也就是说，通过在矩阵中加入一个lambda倍的单位矩阵，限制了所有w的和。这种技术在统计学中也称为缩减。

```python
def ridgeRegres(xMat,yMat,lam=0.2):
    xTx = xMat.T*xMat
    denom = xTx + eye(shape(xMat)[1])*lam
    if linalg.det(denom) == 0.0:
        print "This matrix is singular, cannot do inverse"
        return
    ws = denom.I * (xMat.T*yMat)
    return ws
    
def ridgeTest(xArr,yArr):
    xMat = mat(xArr); yMat=mat(yArr).T
    yMean = mean(yMat,0)
    yMat = yMat - yMean     #to eliminate X0 take mean off of Y
    #regularize X's
    xMeans = mean(xMat,0)   #calc mean then subtract it off
    xVar = var(xMat,0)      #calc variance of Xi then divide by it
    xMat = (xMat - xMeans)/xVar
    numTestPts = 30
    wMat = zeros((numTestPts,shape(xMat)[1]))
    for i in range(numTestPts):
        ws = ridgeRegres(xMat,yMat,exp(i-10))
        wMat[i,:]=ws.T
    return wMat
```

对于lambda，当lambda很小时，回归结果与线性回归相同；当lambda很大时，所有的回归系数都减小为0.在使用时需要根据测试选取一个最合适的lambda。

### 0x05 向前逐步回归

这种方法属于一种贪心方法。贪心策略是每次对某个回归系数进行微小改动，如果改改动能减小误差，则保存改动，否则rollback。此算法的优点是计算复杂度比较低。

```python
def regularize(xMat):#regularize by columns
    inMat = xMat.copy()
    inMeans = mean(inMat,0)   #calc mean then subtract it off
    inVar = var(inMat,0)      #calc variance of Xi then divide by it
    inMat = (inMat - inMeans)/inVar
    return inMat

def stageWise(xArr,yArr,eps=0.01,numIt=100):
    xMat = mat(xArr); yMat=mat(yArr).T
    yMean = mean(yMat,0)
    yMat = yMat - yMean     #can also regularize ys but will get smaller coef
    xMat = regularize(xMat)
    m,n=shape(xMat)
    returnMat = zeros((numIt,n)) #testing code remove
    ws = zeros((n,1)); wsTest = ws.copy(); wsMax = ws.copy()
    for i in range(numIt):
        print ws.T
        lowestError = inf; 
        for j in range(n):
            for sign in [-1,1]:
                wsTest = ws.copy()
                wsTest[j] += eps*sign
                yTest = xMat*wsTest
                rssE = rssError(yMat.A,yTest.A)
                if rssE < lowestError:
                    lowestError = rssE
                    wsMax = wsTest
        ws = wsMax.copy()
        returnMat[i,:]=ws.T
    return returnMat
```

比如下图就是一组训练数据在步长为0.005，1000次迭代情况下的结果：

<br/>

![p8](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/LinearRegression/08.png)

<br/>

对于那些基本没有增长或者增长很少的回归系数，就可以判定为对结果没有贡献而去掉。