---
layout: post
title:  "python机器学习笔记（6）—— AdaBoost"
date:   2017-03-14 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是AdaBoost？

我们可以用多个弱分类器的实例来构建一个强分类器。AdaBoost就是基于这样一个理论来实现它的功能的。弱分类器意味着分类器的分类能力很弱，仅仅强于50%。在算法中会为每个分类器赋予一个权重，每次训练都会改动这个权重。比如对于某个第一次分错了，而第二次分对的样本，算法会减少第一次的权重，增加第二次的权重。其中错误率定义为：

<br/>

![f1](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/ada/f1.gif)

<br/>

然后权重alpha的计算公式是：

<br/>

![f2](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/ada/f2.gif)

<br/>

计算出alpha值后就能对权重向量D进行更新，使得正确分类的样本的权重升高，错误分类的样本的权重降低。D的计算方法如下：

如果某个样本被正确分类：

<br/>

![f3](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/ada/f3.gif)

<br/>

如果某个样本被错误分类：

<br/>

![f4](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/ada/f4.gif)

<br/>

然后再计算出D后，AdaBoost开始下一轮迭代，直到错误率为0或弱分类器的数目达到要求的数目。

- **优点：**泛化错误率低，易编码，无参数调整。
- **缺点：**对离群点敏感。
- **适用数据范围：**数值型和标量型。

### 0x01 基于单层决策树构建弱分类器

就是一个在图中垂直分割判定最佳分割情况的算法。

![gif](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/ada/0_0.gif)

上图是对测试数据的算法运行过程。（实际上不太对，少了个+1与-1位置交换的步骤，不过图片太多了，所以……(=.=)）

```python
def loadSimpData():
    datMat = matrix([[ 1. ,  2.1],
        [ 2. ,  1.1],
        [ 1.3,  1. ],
        [ 1. ,  1. ],
        [ 2. ,  1. ]])
    classLabels = [1.0, 1.0, -1.0, -1.0, 1.0]
    return datMat,classLabels

def stumpClassify(dataMatrix,dimen,threshVal,threshIneq):#just classify the data
    retArray = ones((shape(dataMatrix)[0],1))
    if threshIneq == 'lt':
        retArray[dataMatrix[:,dimen] <= threshVal] = -1.0
    else:
        retArray[dataMatrix[:,dimen] > threshVal] = -1.0
    return retArray
    

def buildStump(dataArr,classLabels,D):
    dataMatrix = mat(dataArr); labelMat = mat(classLabels).T
    m,n = shape(dataMatrix)
    numSteps = 10.0; bestStump = {}; bestClasEst = mat(zeros((m,1)))
    minError = inf #init error sum, to +infinity
    for i in range(n):#loop over all dimensions
        rangeMin = dataMatrix[:,i].min(); rangeMax = dataMatrix[:,i].max();
        stepSize = (rangeMax-rangeMin)/numSteps
        for j in range(-1,int(numSteps)+1):#loop over all range in current dimension
            for inequal in ['lt', 'gt']: #go over less than and greater than
                threshVal = (rangeMin + float(j) * stepSize)
                predictedVals = stumpClassify(dataMatrix,i,threshVal,inequal)#call stump classify with i, j, lessThan
                errArr = mat(ones((m,1)))
                errArr[predictedVals == labelMat] = 0
                weightedError = D.T*errArr  #calc total error multiplied by D
                #print "split: dim %d, thresh %.2f, thresh ineqal: %s, the weighted error is %.3f" % (i, threshVal, inequal, weightedError)
                if weightedError < minError:
                    minError = weightedError
                    bestClasEst = predictedVals.copy()
                    bestStump['dim'] = i
                    bestStump['thresh'] = threshVal
                    bestStump['ineq'] = inequal
    return bestStump,minError,bestClasEst
```

### 0x03 完整的算法

上面的是单步，然后与下面的结合就是完整的代码。

```python
def adaBoostTrainDS(dataArr,classLabels,numIt=40):
    weakClassArr = []
    m = shape(dataArr)[0]
    D = mat(ones((m,1))/m)   #init D to all equal
    aggClassEst = mat(zeros((m,1)))
    for i in range(numIt):
        bestStump,error,classEst = buildStump(dataArr,classLabels,D)#build Stump
        #print "D:",D.T
        alpha = float(0.5*log((1.0-error)/max(error,1e-16)))#calc alpha, throw in max(error,eps) to account for error=0
        bestStump['alpha'] = alpha  
        weakClassArr.append(bestStump)                  #store Stump Params in Array
        #print "classEst: ",classEst.T
        expon = multiply(-1*alpha*mat(classLabels).T,classEst) #exponent for D calc, getting messy
        D = multiply(D,exp(expon))                              #Calc New D for next iteration
        D = D/D.sum()
        #calc training error of all classifiers, if this is 0 quit for loop early (use break)
        aggClassEst += alpha*classEst
        #print "aggClassEst: ",aggClassEst.T
        aggErrors = multiply(sign(aggClassEst) != mat(classLabels).T,ones((m,1)))
        errorRate = aggErrors.sum()/m
        print "total error: ",errorRate
        if errorRate == 0.0: break
    return weakClassArr,aggClassEst
```

### 0x04 使用分类器


```python
def adaClassify(datToClass,classifierArr):
    dataMatrix = mat(datToClass)#do stuff similar to last aggClassEst in adaBoostTrainDS
    m = shape(dataMatrix)[0]
    aggClassEst = mat(zeros((m,1)))
    for i in range(len(classifierArr)):
        classEst = stumpClassify(dataMatrix,classifierArr[i]['dim'],\
                                 classifierArr[i]['thresh'],\
                                 classifierArr[i]['ineq'])#call stump classify
        aggClassEst += classifierArr[i]['alpha']*classEst
        print aggClassEst
    return sign(aggClassEst)
```
