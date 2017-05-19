---
layout: post
title:  "python机器学习笔记（5）—— SVM支持向量机"
date:   2017-03-14 11:49:45 +0200
categories: meachinelearning
published: true
---
### 0x00 什么是SVM？

SVM即Support Vector Machine，支持向量机，在一般情况下是一个二分类分类器。相比Logistic回归，SVM不是向某一函数作拟合，而是直接生成一个分割超平面，并且效率更高。只要在训练数据中找到了支持向量，就可以利用这些支持向量进行分类，这样同时也减少了数据量。

- **优点：**泛化错误率低，计算开销不大，结果易解释。
- **缺点：**对参数调节和核函数的选择敏感，原始分类器不加修改仅适用于处理二类问题。
- **适用数据范围：**数值型和标量型。

### 0x01 分类器算法的推导

首先我们回想到Logistic回归，同样是对两类数据进行分类，在图中画出两类数据的分界线。我们设分界的超平面（现在是直线）的公式为![f1](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f1.gif)，我们很容易得到某个点到直线距离的函数间隔![f2](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f2.gif)，几何间隔![f3](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f3.gif)。

<br/>

<br/>

现在我们考虑一个问题，如何让所有点中，离这个分分割面的距离最近的点，里这个分割面最远。这个句话听起来有点绕，但它就是这个意思。也就是说，我们考虑这样的情况：

![f4](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f4.gif)

<br/>

<br/>

对于这种情况求解是非常困难的，所以我们采用一种变换方式，将它变成我们易于求解形式。首先我们假设所有支持向量（即离分割超平面最近的点）到分割超平面的距离为1，那么所有非支持向量到分割超平面的距离就大于1。然后我们考虑到![f5](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f5.gif)等价于求解![f6](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f6.gif)。那么，我们可以得到这样的式子：

<br/>

<br/>

![f7](http://ofnd3snod.bkt.clouddn.com/f7.png)

![f8](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f8.png)

<br/>

<br/>

其中s.t.表示限制条件。然后就可以利用拉格朗日对偶法求最大值，具体推导公式就不在这里细写，直接列出其中推导出有用的公式和需要求解的公式:

<br/>

<br/>

![f9](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f9.png)

![f10](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f10.png)

![f11](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f11.png)

<br/>

<br/>

其中上面那个求最大值的就是我们需要求得目标函数，通过这个函数我们求得阿尔法，从而求出w和b，得到了最后的结果。这里最后加上b的求法。思想是在超平面上方和下方的支持向量到超平面的距离一致。

<br/>

<br/>

![f12](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f12.png)

<br/>

<br/>

### 0x02 SMO高效算法

回到上面用拉格朗日对偶推导出来的公式：

<br/>

<br/>

![f9](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f9.png)

<br/>

<br/>

我们可以发现，如果我们一次迭代中只改变一个阿尔法的值，那么上面的等式会不满足约束条件，那么我们考虑一次同时改变两个阿尔法的值，保证它们的和为一个常数.同时我们为了允许存在少数分类错误的点存在空间中，增加一个松弛变量C，使阿尔法小于C。那么，我们可以推算出他们的范围：

<br/>

<br/>

当它们异号时

<br/>

<br/>

![f13](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f13.png)

<br/>

<br/>

当它们同号时

<br/>

<br/>

![f14](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f14.png)

<br/>

<br/>

然后我们设一条公式

<br/>

<br/>

![f15](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f15.png)

<br/>

<br/>

结合这条公式，并且将a1用a2来表示带入求最大值的式子中，可以推导出这样的一条公式

<br/>

<br/>

![f16](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f16.png)

<br/>

<br/>

其中![f17](http://ofnd3snod.bkt.clouddn.com/f17.png)。特殊情况下eta可能不为正，处理起来非常麻烦。不过一般不会出现，这里不做讨论。

<br/>

<br/>

那么b应该怎么求呢。

<br/>

<br/>

![f18](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f18.jpg)

<br/>

<br/>

其中界内指的就是在0与C之间。

<br/>

<br/>

上述内容参考[支持向量机（五）SMO算法](http://www.cnblogs.com/jerrylead/archive/2011/03/18/1988419.html).

<br/>

<br/>

### 0x03 核函数

大部分的数据往往是线性不可分的，这种时候就需要使用核函数将数据从低维度映射到高维度。比如对于

<br/>

<br/>

![f19](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f19.png)

<br/>

<br/>

我们可以通过做乘积的方式增加它的维度

<br/>

<br/>

![f20](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f20.png)

<br/>

<br/>

比如上面的例子，数据就从二维变成了五维。

<br/>

<br/>

常用的核函数是这个，高斯核函数

<br/>

<br/>

![f21](http://ofnd3snod.bkt.clouddn.com/blog/meachineleaning/SVM/f21.png)

### 0x04 代码实现

结合上面这些公式看代码就相对好懂了。

```python
def kernelTrans(X, A, kTup): #calc the kernel or transform data to a higher dimensional space
    m,n = shape(X)
    K = mat(zeros((m,1)))
    if kTup[0]=='lin': K = X * A.T   #linear kernel
    elif kTup[0]=='rbf':
        for j in range(m):
            deltaRow = X[j,:] - A
            K[j] = deltaRow*deltaRow.T
        K = exp(K/(-1*kTup[1]**2)) #divide in NumPy is element-wise not matrix like Matlab
    else: raise NameError('Houston We Have a Problem -- \
    That Kernel is not recognized')
    return K

class optStruct:
    def __init__(self,dataMatIn, classLabels, C, toler, kTup):  # Initialize the structure with the parameters 
        self.X = dataMatIn
        self.labelMat = classLabels
        self.C = C
        self.tol = toler
        self.m = shape(dataMatIn)[0]
        self.alphas = mat(zeros((self.m,1)))
        self.b = 0
        self.eCache = mat(zeros((self.m,2))) #first column is valid flag
        self.K = mat(zeros((self.m,self.m)))
        for i in range(self.m):
            self.K[:,i] = kernelTrans(self.X, self.X[i,:], kTup)
        
def calcEk(oS, k):
    fXk = float(multiply(oS.alphas,oS.labelMat).T*oS.K[:,k] + oS.b)
    Ek = fXk - float(oS.labelMat[k])
    return Ek
        
def selectJ(i, oS, Ei):         #this is the second choice -heurstic, and calcs Ej
    maxK = -1; maxDeltaE = 0; Ej = 0
    oS.eCache[i] = [1,Ei]  #set valid #choose the alpha that gives the maximum delta E
    validEcacheList = nonzero(oS.eCache[:,0].A)[0]
    if (len(validEcacheList)) > 1:
        for k in validEcacheList:   #loop through valid Ecache values and find the one that maximizes delta E
            if k == i: continue #don't calc for i, waste of time
            Ek = calcEk(oS, k)
            deltaE = abs(Ei - Ek)
            if (deltaE > maxDeltaE):
                maxK = k; maxDeltaE = deltaE; Ej = Ek
        return maxK, Ej
    else:   #in this case (first time around) we don't have any valid eCache values
        j = selectJrand(i, oS.m)
        Ej = calcEk(oS, j)
    return j, Ej

def updateEk(oS, k):#after any alpha has changed update the new value in the cache
    Ek = calcEk(oS, k)
    oS.eCache[k] = [1,Ek]
        
def innerL(i, oS):
    Ei = calcEk(oS, i)
    if ((oS.labelMat[i]*Ei < -oS.tol) and (oS.alphas[i] < oS.C)) or ((oS.labelMat[i]*Ei > oS.tol) and (oS.alphas[i] > 0)):
        j,Ej = selectJ(i, oS, Ei) #this has been changed from selectJrand
        alphaIold = oS.alphas[i].copy(); alphaJold = oS.alphas[j].copy();
        if (oS.labelMat[i] != oS.labelMat[j]):
            L = max(0, oS.alphas[j] - oS.alphas[i])
            H = min(oS.C, oS.C + oS.alphas[j] - oS.alphas[i])
        else:
            L = max(0, oS.alphas[j] + oS.alphas[i] - oS.C)
            H = min(oS.C, oS.alphas[j] + oS.alphas[i])
        if L==H: print "L==H"; return 0
        eta = 2.0 * oS.K[i,j] - oS.K[i,i] - oS.K[j,j] #changed for kernel
        if eta >= 0: print "eta>=0"; return 0
        oS.alphas[j] -= oS.labelMat[j]*(Ei - Ej)/eta
        oS.alphas[j] = clipAlpha(oS.alphas[j],H,L)
        updateEk(oS, j) #added this for the Ecache
        if (abs(oS.alphas[j] - alphaJold) < 0.00001): print "j not moving enough"; return 0
        oS.alphas[i] += oS.labelMat[j]*oS.labelMat[i]*(alphaJold - oS.alphas[j])#update i by the same amount as j
        updateEk(oS, i) #added this for the Ecache                    #the update is in the oppostie direction
        b1 = oS.b - Ei- oS.labelMat[i]*(oS.alphas[i]-alphaIold)*oS.K[i,i] - oS.labelMat[j]*(oS.alphas[j]-alphaJold)*oS.K[i,j]
        b2 = oS.b - Ej- oS.labelMat[i]*(oS.alphas[i]-alphaIold)*oS.K[i,j]- oS.labelMat[j]*(oS.alphas[j]-alphaJold)*oS.K[j,j]
        if (0 < oS.alphas[i]) and (oS.C > oS.alphas[i]): oS.b = b1
        elif (0 < oS.alphas[j]) and (oS.C > oS.alphas[j]): oS.b = b2
        else: oS.b = (b1 + b2)/2.0
        return 1
    else: return 0

def smoP(dataMatIn, classLabels, C, toler, maxIter,kTup=('lin', 0)):    #full Platt SMO
    oS = optStruct(mat(dataMatIn),mat(classLabels).transpose(),C,toler, kTup)
    iter = 0
    entireSet = True; alphaPairsChanged = 0
    while (iter < maxIter) and ((alphaPairsChanged > 0) or (entireSet)):
        alphaPairsChanged = 0
        if entireSet:   #go over all
            for i in range(oS.m):        
                alphaPairsChanged += innerL(i,oS)
                print "fullSet, iter: %d i:%d, pairs changed %d" % (iter,i,alphaPairsChanged)
            iter += 1
        else:#go over non-bound (railed) alphas
            nonBoundIs = nonzero((oS.alphas.A > 0) * (oS.alphas.A < C))[0]
            for i in nonBoundIs:
                alphaPairsChanged += innerL(i,oS)
                print "non-bound, iter: %d i:%d, pairs changed %d" % (iter,i,alphaPairsChanged)
            iter += 1
        if entireSet: entireSet = False #toggle entire set loop
        elif (alphaPairsChanged == 0): entireSet = True  
        print "iteration number: %d" % iter
    return oS.b,oS.alphas
```
