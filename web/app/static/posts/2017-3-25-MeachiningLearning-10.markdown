---
layout: post
title:  "python机器学习笔记（10）—— Apriori关联分析"
date:   2017-03-25 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是Apriori算法？

Apriori算法通过分析数据各项的支持度来判断数据之间的关联性。某子集置信度就是某子集合在所有集合中出现的次数比上所有集合的数目。比如对于如下数据集：

```python
data = [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]
```

我们可以利用算法判断哪些数字组合是经常出现的：

```python
[[frozenset([1]), frozenset([3]), frozenset([2]), frozenset([5])], [frozenset([1, 3]), frozenset([2, 5]), frozenset([2, 3]), frozenset([3, 5])], [frozenset([2, 3, 5])], []]
```

以上是出现概率大于0.5的数据集。

<br/>

- **优点：**容易实现。
- **缺点：**大数据集下运算较慢。
- **适用数据范围：**数值型或标量型。

### 0x01 基础实现

如果存在一个包含N个元素的集合，那么我们或许需要对二的N次方减一的可能组合进行判断，那么这样的运算量是非常庞大的。但实际上容易推出，如果一个集合是非频繁的，那么它所存在的集合也是非频繁的。基于这个思想可以降低运算量。

```python
def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
                
    C1.sort()
    return map(frozenset, C1)#use frozen set so we
                            #can use it as a key in a dict    

def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                if not ssCnt.has_key(can): ssCnt[can]=1
                else: ssCnt[can] += 1
    numItems = float(len(D))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key]/numItems
        if support >= minSupport:
            retList.insert(0,key)
        supportData[key] = support
    return retList, supportData

def aprioriGen(Lk, k): #creates Ck
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk): 
            L1 = list(Lk[i])[:k-2]; L2 = list(Lk[j])[:k-2]
            L1.sort(); L2.sort()
            if L1==L2: #if first k-2 elements are equal
                retList.append(Lk[i] | Lk[j]) #set union
    return retList

def apriori(dataSet, minSupport = 0.5):
    C1 = createC1(dataSet)
    D = map(set, dataSet)
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0):
        Ck = aprioriGen(L[k-2], k)
        Lk, supK = scanD(D, Ck, minSupport)#scan DB to get Lk
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData
```

    这里真忍不住要吐个槽。作者为什么要把k的初值设成2，然后所有用k的地方都写成k-2呢？其实k就是指向频繁集集合的最后一个元素的指针，直接把k初值设成0，然后所有地方直接用k不好么？

<br/>

算法大概是这样一个流程：

- 1.首先使用`createC1()`函数获取到数据集中的最小元素集合。
- 2.然后使用`scanD()`来判断这些元素集合是否有足够高的置信度，并选择有足够高的置信度的集合。
- 3.然后进入循环，不断用这些集合合并生成更复杂的集合并判断置信度，直到所有集合被生成。

### 0x02 从频繁集中挖掘规则

接下来的算法就相当有趣了。我们可以利用上面算出来的频繁集，判断各个集合的关联规则。在算法中，我们利用到贝叶斯公式：

<br/>

![f0](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/apriori/f0.gif)

<br/>

```python
def generateRules(L, supportData, minConf=0.7):  #supportData is a dict coming from scanD
    bigRuleList = []
    for i in range(1, len(L)):#only get the sets with two or more items
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            if (i > 1):
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList         

def calcConf(freqSet, H, supportData, brl, minConf=0.7):
    prunedH = [] #create new list to return
    for conseq in H:
        conf = supportData[freqSet]/supportData[freqSet-conseq] #calc confidence
        if conf >= minConf: 
            print freqSet-conseq,'-->',conseq,'conf:',conf
            brl.append((freqSet-conseq, conseq, conf))
            prunedH.append(conseq)
    return prunedH

def rulesFromConseq(freqSet, H, supportData, brl, minConf=0.7):
    m = len(H[0])
    if (len(freqSet) > (m + 1)): #try further merging
        Hmp1 = aprioriGen(H, m+1)#create Hm+1 new candidates
        Hmp1 = calcConf(freqSet, Hmp1, supportData, brl, minConf)
        if (len(Hmp1) > 1):    #need at least two sets to merge
            rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)
```

`calcConf()`用来判断某频繁集中的元素能否与输入的子集构成相关关系。

`rulesFromConseq()`用来将子集拓展。

`generateRules()`用来获取频繁集。

<br/>

运行结果如下：

```python
import apriori

data = apriori.loadDataSet()

L,suppData = apriori.apriori(data,0.5)

rules = apriori.generateRules(L,suppData,minConf=0.5)

print rules

# frozenset([3]) --> frozenset([1]) conf: 0.666666666667
# frozenset([1]) --> frozenset([3]) conf: 1.0
# frozenset([5]) --> frozenset([2]) conf: 1.0
# frozenset([2]) --> frozenset([5]) conf: 1.0
# frozenset([3]) --> frozenset([2]) conf: 0.666666666667
# frozenset([2]) --> frozenset([3]) conf: 0.666666666667
# frozenset([5]) --> frozenset([3]) conf: 0.666666666667
# frozenset([3]) --> frozenset([5]) conf: 0.666666666667
# [(frozenset([3]), frozenset([1]), 0.6666666666666666), (frozenset([1]), frozenset([3]), 1.0), (frozenset([5]), frozenset([2]), 1.0), (frozenset([2]), frozenset([5]), 1.0), (frozenset([3]), frozenset([2]), 0.6666666666666666), (frozenset([2]), frozenset([3]), 0.6666666666666666), (frozenset([5]), frozenset([3]), 0.6666666666666666), (frozenset([3]), frozenset([5]), 0.6666666666666666)]
```