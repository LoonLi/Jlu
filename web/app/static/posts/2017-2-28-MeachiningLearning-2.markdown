---
layout: post
title:  "python机器学习笔记（2）—— ID3决策树"
date:   2017-02-28 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是ID3？

ID3算法（Iterative Dichotomiser 3 迭代二叉树3代）是一个由Ross Quinlan发明的用于决策树的算法。

- **优点：**复杂度比k邻近算法低。
- **缺点：**可能产生过度匹配问题。
- **适用数据范围：**数值型，标量型。

这个算法是建立在奥卡姆剃刀的基础上：越是小型的决策树越优于大的决策树（简单理论）。尽管如此，该算法也不是总是生成最小的树形结构。而是一个启发式算法。

ID3算法通过计算计算信息熵来计算出最优的树结构。信息熵的概念参见[这里](https://zh.wikipedia.org/wiki/%E7%86%B5_(%E4%BF%A1%E6%81%AF%E8%AE%BA))。

算法的思路大概是这样的：

- 1.标签集中遍历标签。
- 2.找到在该情况下最优的划分。
- 3.生成当前情况的树。
- 4.回到1，直到整个树生成完成。

### 0x01 计算信息熵

    以下代码中dataSet均以dataSet = {[feature1,...,featureN,result],[...],...}为格式。举个例子就是
    dataSet = [[1,1,'yes'],
    [1,1,'yes'],
    [0,1,'no'],
    [1,0,'no'],
    [0,1,'no']
    ]
    labels = ['no surfacing','flippers']

```python
#数据集以数据加标签形式为格式
def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel]+=1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob*log(prob,2)
    return shannonEnt
```

简单地说，信息熵越大，则说明该介质携带的信息量越大。比如一个汉字的信息熵就比一个英文字母的信息熵要大。

### 0x02 划分数据集

如上面所说，需要找到在某个属性作为key时，value的熵最小的情况。所以需要做的一项工作就是把这个作为key的属性从数据集中抽取出来。

```python
#划分数据集，就是剔出axis列的对应特征值为value的向量
def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]
            reducedFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet
```

然后就是计算在某个属性作为key时，value的熵最小的情况。

```python
#选择最佳数据集划分方式
def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0
    bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        #set()可以将元组转变成无序集合，即去除相同元素
        uniqueVals = set(featList)
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob*calcShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy
        if (infoGain > bestInfoGain):
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature
```

### 0x04 递归生成决策树

经过上面的准备，生成决策树的代码就很好写了。

```python
#处理当用完所有特征信息时仍然不能确定分类的情况
#返回数量最多的类别
def majorityCnt(classList):
    classCount={}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote]=0
        classCount[vote] += 1
        sortedClassCount = sorted(classCount.iteritems(),key=lambda x:x[1],reverse = True)
        return sortedClassCount[0][0]

#创建决策树
def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    if len(dataSet[0]) == 1:
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value), subLabels)
    return myTree
```

### 0x04 使用决策树执行分类

相对k邻近算法,决策树的使用就非常直观了，从根节点向下走就能得到结果。

```python
def classify(inputTree,featLabels,testVec):
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    key = testVec[featIndex]
    valueOfFeat = secondDict[key]
    if isinstance(valueOfFeat, dict): 
        classLabel = classify(valueOfFeat, featLabels, testVec)
    else: classLabel = valueOfFeat
    return classLabel
```
