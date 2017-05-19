---
layout: post
title:  "python机器学习笔记（11）—— FP-growth"
date:   2017-03-28 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是FP-growth算法？

在使用google时，我们在输入关键词后，它会自动给我们可能的补全项。FP-growth就可以实现这个功能。FP-growth是用于高效发现频繁集的算法。它两次扫描数据，其中第一次是构建FP树，第二次是从中挖掘频繁项集。

- **优点：**速度一般较快。
- **缺点：**大数据集下运算较慢。
- **适用数据范围：**数值型或标量型。

### 0x01 构建FP树

FP树的特点是可能会出现重复的项，并且重复项会有指针相连。树的容器结构如下：

```python
class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode      #needs to be updated
        self.children = {} 
    
    def inc(self, numOccur):
        self.count += numOccur
        
    def disp(self, ind=1):
        print '  '*ind, self.name, ' ', self.count
        for child in self.children.values():
            child.disp(ind+1)
```

然后是构建树的代码：

```python
def createTree(dataSet, minSup=1): #create FP-tree from dataset but don't mine
    headerTable = {}
    #go over dataSet twice
    for trans in dataSet:#first pass counts frequency of occurance
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    for k in headerTable.keys():  #remove items not meeting minSup
        if headerTable[k] < minSup: 
            del(headerTable[k])
    freqItemSet = set(headerTable.keys())
    #print 'freqItemSet: ',freqItemSet
    if len(freqItemSet) == 0: return None, None  #if no items meet min support -->get out
    for k in headerTable:
        headerTable[k] = [headerTable[k], None] #reformat headerTable to use Node link 
    #print 'headerTable: ',headerTable
    retTree = treeNode('Null Set', 1, None) #create tree
    for tranSet, count in dataSet.items():  #go through dataset 2nd time
        localD = {}
        for item in tranSet:  #put transaction items in order
            if item in freqItemSet:
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)#populate tree with ordered freq itemset
    return retTree, headerTable #return tree and header table

def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:#check if orderedItems[0] in retTree.children
        inTree.children[items[0]].inc(count) #incrament count
    else:   #add items[0] to inTree.children
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None: #update header table 
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:#call updateTree() with remaining ordered items
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)
        
def updateHeader(nodeToTest, targetNode):   #this version does not use recursion
    while (nodeToTest.nodeLink != None):    #Do not use recursion to traverse a linked list!
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode
```

`createTree()`首先计算并移除不满足支持度的项目，然后初始化头指针列表，利用`updateTree()`函数生成树节点。

<br/>

`updateTree()`则首先判断项目是否在其子节点中，在则增加子节点计数；不在则生成该子节点，使用`updateHeader()`函数生成节点间指针，并对子节点递归。

<br/>

`updataHeader()`是一个简单的循环，找到该节点的最后一次重复位置。

<br/>

测试结果如下：

```python
import fpGrowth

simpDat = fpGrowth.loadSimpDat()
print simpDat
# [['r', 'z', 'h', 'j', 'p'], ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'], ['z'], ['r', 'x', 'n', 'o', 's'], ['y', 'r', 'x', 'z', 'q', 't', 'p'], ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]

initSet = fpGrowth.createInitSet(simpDat)
print initSet
# {frozenset(['e', 'm', 'q', 's', 't', 'y', 'x', 'z']): 1, frozenset(['x', 's', 'r', 'o', 'n']): 1, frozenset(['s', 'u', 't', 'w', 'v', 'y', 'x', 'z']): 1, frozenset(['q', 'p', 'r', 't', 'y', 'x', 'z']): 1, frozenset(['h', 'r', 'z', 'p', 'j']): 1, frozenset(['z']): 1}

myFPtree, myHeaderTab = fpGrowth.createTree(initSet,3)
myFPtree.disp()
   # Null Set   1
   #   x   1
   #     s   1
   #       r   1
   #   z   5
   #     x   3
   #       y   3
   #         s   2
   #           t   2
   #         r   1
   #           t   1
   #     r   1
```

### 0x02 从FP树中挖掘频繁规则

首先我们需要得到给定某元素结尾的所有路径。

```python
def ascendTree(leafNode, prefixPath): #ascends from leaf node to root
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)
    
def findPrefixPath(basePat, treeNode): #treeNode comes from header table
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1: 
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats
```

代码还是相当直观的，就不作解释（作者写了个卵用没有的`basePat`变量是方便读者理解么……）。

<br/>

然后递归查找频繁集：

```python
def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1])]#(sort header table)
    for basePat in bigL:  #start from bottom of header table
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        #print 'finalFrequent Item: ',newFreqSet    #append to set
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        #print 'condPattBases :',basePat, condPattBases
        #2. construct cond FP-tree from cond. pattern base
        myCondTree, myHead = createTree(condPattBases, minSup)
        #print 'head from conditional tree: ', myHead
        if myHead != None: #3. mine cond. FP-tree
            #print 'conditional tree for: ',newFreqSet
            #myCondTree.disp(1)            
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)
```

比较难以理解的部分可能是`preFix`这个参数。这个参数在每次递归之前都会加入用于生成上面所说的 *给定某元素结尾的所有路径* 的这个元素，然后把加入该元素后的集合append到返回参数中。

<br/>

运行效果是这样的：

```python
freqItems = []
fpGrowth.mineTree(myFPtree, myHeaderTab, 3, set([]), freqItems)
# conditional tree for:  set(['y'])
#    Null Set   1
#      x   3
#        z   3
# conditional tree for:  set(['y', 'z'])
#    Null Set   1
#      x   3
# conditional tree for:  set(['s'])
#    Null Set   1
#      x   3
# conditional tree for:  set(['t'])
#    Null Set   1
#      y   3
#        x   3
#          z   3
# conditional tree for:  set(['x', 't'])
#    Null Set   1
#      y   3
# conditional tree for:  set(['z', 't'])
#    Null Set   1
#      y   3
#        x   3
# conditional tree for:  set(['x', 'z', 't'])
#    Null Set   1
#      y   3
# conditional tree for:  set(['x'])
#    Null Set   1
#      z   3

print freqItems
# [set(['y']), set(['y', 'x']), set(['y', 'z']), set(['y', 'x', 'z']), set(['s']), set(['x', 's']), set(['t']), set(['y', 't']), set(['x', 't']), set(['y', 'x', 't']), set(['z', 't']), set(['y', 'z', 't']), set(['x', 'z', 't']), set(['y', 'x', 'z', 't']), set(['r']), set(['x']), set(['x', 'z']), set(['z'])]

```