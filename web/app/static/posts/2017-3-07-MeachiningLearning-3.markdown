---
layout: post
title:  "python机器学习笔记（3）—— 朴素贝叶斯"
date:   2017-03-07 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是朴素贝叶斯？

朴素贝叶斯分类器是一系列以假设特征之间强（朴素）独立下运用贝叶斯定理为基础的简单概率分类器。该算法中应用了 **条件概率** 和 **贝叶斯公式**的相关知识，这篇博客不做详细介绍。

- **优点：**在数据较小的情况下仍然有效，可以处理多类别问题。
- **缺点：**对于输入数据比较敏感。
- **适用数据范围：**标量型。

朴素贝叶斯算法做出了以下假设：（1）数据的每个特征是相互独立的。（2）每个特征同等重要。显然这些假设都是理想化的，在现实的数据中不太可能实现，但即使如此，该算法依旧能取得相当好的运算结果。

以下是贝叶斯公式：P(A|B)=P(B|A)P(A)/P(B)

对于式子中的A即是输入的分类结果，B是输入的特征。最终求出的结果P(A|B)即是在输入为B的情况下，分类为A的概率。算法在计算过程中会得出各个分类对应的概率，其中最大的值即使对应的分类概率。

但其实上面一段的说明是不太准确的但更好理解。因为对于每次计算P(B)都是一样的，所以在算法中只计算到P(B|A)P(A)即可。

在算法中还会利用训练数据生成模式向量，用来计算P(B|A)。这个有点抽象，看代码比较好明白。

经过上面的分析算法的逻辑也就很清晰了：

- 1.获取训练数据的特征和分类。
- 2.生成模式向量。
- 3.计算每个特征在每个分类下的概率P(Bx|Ax)及某个分类的概率P(Ax)。
- 4.比较每种情况的概率的大小，得出最终结果。

接下来看一个文本分类的实例。

### 0x01 构建词向量

比如说存在一个词汇表['a','b','c','d']，而一篇文档有词汇['a','d']，那么这个文章对应的词向量就是[1,0,0,1]。以下是转化的代码：

```python
#用作生成测试数据
def loadDataSet():
    postingList=[['my', 'dog', 'has', 'flea', 'problems', 'help', 'please'],
                 ['maybe', 'not', 'take', 'him', 'to', 'dog', 'park', 'stupid'],
                 ['my', 'dalmation', 'is', 'so', 'cute', 'I', 'love', 'him'],
                 ['stop', 'posting', 'stupid', 'worthless', 'garbage'],
                 ['mr', 'licks', 'ate', 'my', 'steak', 'how', 'to', 'stop', 'him'],
                 ['quit', 'buying', 'worthless', 'dog', 'food', 'stupid']]
    classVec = [0,1,0,1,0,1]   #其中0是不和谐词汇,1是和谐词汇
    return postingList,classVec
                 
def createVocabList(dataSet):
    vocabSet = set([]) 
    for document in dataSet:
        #集合可以进行并操作
        vocabSet = vocabSet | set(document) 
    return list(vocabSet)

def setOfWords2Vec(vocabList, inputSet):
    returnVec = [0]*len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
        else: print "the word: %s is not in my Vocabulary!" % word
    return returnV
```

在以上的代码中，函数`setOfWords2Vec(vocabList, inputSet)`中有一句`returnVec[vocabList.index(word)] = 1`。在这种情况下，每个若有多个相同的词出现对结果是没有影响的。这称为 **词集模型** 。如果想利用多次出现的属性，则可以改成以下代码`returnVec[vocabList.index(word)] += 1`。这种情况则称为 **词袋模型**。

### 0x02 编写训练函数

训练函数可以计算出每个词汇对应分类的概率p。即如果一篇文章出出现了这个词汇，那么这篇文章属于该分类的概率会增加p。（不准确描述）

```python
def trainNB0(trainMatrix,trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = sum(trainCategory)/float(numTrainDocs)
    #为了避免某个概率计算结果为零，将初始矩阵设置为1
    p0Num = ones(numWords); p1Num = ones(numWords) 
    #为了避免某个概率计算结果为零，将某类词汇总数初始设置为2 
    p0Denom = 2.0; p1Denom = 2.0                     
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    #为了避免数值过小被约成0，用Log来计算
    p1Vect = log(p1Num/p1Denom)         
    p0Vect = log(p0Num/p0Denom)      
    return p0Vect,p1Vect,pAbusive
```

如上注释，为了避免有概率计算结果为0的情况，做了几个处理。

### 0x03 分类

然后就可以利用贝叶斯公式计算概率了。以下是分类函数和测试函数。

```python
def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    p1 = sum(vec2Classify * p1Vec) + log(pClass1)
    p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)
    if p1 > p0:
        return 1
    else: 
        return 0
    
def testingNB():
    listOPosts,listClasses = loadDataSet()
    myVocabList = createVocabList(listOPosts)
    trainMat=[]
    for postinDoc in listOPosts:
        trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
    p0V,p1V,pAb = trainNB0(array(trainMat),array(listClasses))
    testEntry = ['love', 'my', 'dalmation']
    thisDoc = array(setOfWords2Vec(myVocabList, testEntry))
    print testEntry,'classified as: ',classifyNB(thisDoc,p0V,p1V,pAb)
    testEntry = ['stupid', 'garbage']
    thisDoc = array(setOfWords2Vec(myVocabList, testEntry))
    print testEntry,'classified as: ',classifyNB(thisDoc,p0V,p1V,pAb)
```
