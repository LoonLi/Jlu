---
layout: post
title:  "利用selenium+PhantomJS爬取ajax网页"
date:   2017-01-19 11:49:45 +0200
categories: python
published: true
---
最近遇到了个利用ajax写的专利信息网站，正好用来练手写了这个爬虫。

## 0x00 准备工作
使用 `pip install selenium`安装好该包，并去 *PhantomJS*官网下载其本体，解压后将exe文件放入python的系统路径中。为了方便调试，下载 *chromedirver*使用chrome浏览器调试（Firefox也可以）。

## 0x01 原理说明
PhantomJS是一个模拟浏览器，由于不用分析画面速度相对较快。使用以下语句后就可以对driver进行操作：

``` python
from selenium import webdriver
driver = webdriver.PhantomJS() #调试时用 driver=webdirver.Chrome()
driver.get(url)
```

然后就能够用driver模拟浏览器的各种操作。

### 元素定位
driver本身提供了元素定位的方法。

单个元素选取

```
find_element_by_id

find_element_by_name

find_element_by_xpath

find_element_by_link_text

find_element_by_partial_link_text

find_element_by_tag_name

find_element_by_class_name

find_element_by_css_selector

```

多个元素选取

```
find_elements_by_name

find_elements_by_xpath

find_elements_by_link_text

find_elements_by_partial_link_text

find_elements_by_tag_name

find_elements_by_class_name

find_elements_by_css_selector

```

另外还可以利用 By 类来确定哪种选择方式

```
from selenium.webdriver.common.by import By

driver.find_element(By.XPATH, '//button[text()="Some text"]')
driver.find_elements(By.XPATH, '//button')
```

By 类的一些属性如下

```
ID = "id"
XPATH = "xpath"
LINK_TEXT = "link text"
PARTIAL_LINK_TEXT = "partial link text"
NAME = "name"
TAG_NAME = "tag name"
CLASS_NAME = "class name"
CSS_SELECTOR = "css selector"
```

用法都相当直观，去看一下python源代码马上就能明白。

## 元素操作
选取了元素后就可以对元素进行操作了，例如：

``` python
driver.find_element_by_id('companyDetail').click()
```
以上代码就相当于对id为comanyDetail的元素进行点击操作。
[http://cuiqingcai.com/2599.html](http://cuiqingcai.com/2599.html)这个站点讲的很详细，可以去看看。
此外，用`driver.page_source`就可以获得页面源码。

## 0x02 页面等待
有三种基本策略，第一种是用sleep()强制等待。当然这种效率非常低不推荐使用。另外两种是seleninm提供的隐式等待和显式等待。

### 隐式等待
在访问页面后，都会固定等待一个时间，除非网页已经加载好，然后再进行操作，否则抛出异常。

``` python
# -*- coding: utf-8 -*-
from selenium import webdriver

driver = webdriver.Firefox()
driver.implicitly_wait(30)  # 隐性等待，最长等30秒
driver.get('https://huilansame.github.io')

print driver.current_url
driver.quit()
```

### 显示等待
这种方法更加灵活，可以指定一个页面元素进行等待，直到该元素被加载成功。

``` python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.implicitly_wait(10)  # 隐性等待和显性等待可以同时用，但要注意：等待的最长时间取两者之中的大者
driver.get('https://huilansame.github.io')
locator = (By.LINK_TEXT, 'CSDN')

try:
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    print driver.find_element_by_link_text('CSDN').get_attribute('href')
finally:
    driver.close()
```
以上内容参考[https://huilansame.github.io/huilansame.github.io/archivers/sleep-implicitlywait-wait](https://huilansame.github.io/huilansame.github.io/archivers/sleep-implicitlywait-wait)

## 0x03 实战
基本知识就是那么多，看看应该怎么实用。对于[http://www.neeq.com.cn/nq/detailcompany.html?companyCode=430002](http://www.neeq.com.cn/nq/detailcompany.html?companyCode=430002)这个网站，可以发现它是基于post去返回信息的，所以直接改url就能找到信息。其次利用标签的各个信息进行元素定位，就可已完成页面的爬取。

``` python
#coding=UTF-8
import urllib2
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

db = MySQLdb.connect('127.0.0.1','root','********','****')
cursor =  db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
sentense1 = 'INSERT INTO survey VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'
sentense2 = 'INSERT INTO shareholder VALUES ("%s","%s","%s","%s","%s")'
sentense3 = 'INSERT INTO finance VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'
driver = webdriver.PhantomJS()
url = 'http://www.neeq.com.cn/nq/detailcompany.html?companyCode='
try_count = 0

count = 430002

while count<870700:
	driver.get(url+str(count))
	company_id = 0
	locator = (By.XPATH,"//li[@id='companyDetail']")
	try:
		WebDriverWait(driver,3).until(EC.presence_of_element_located(locator))
	except Exception as e:
		print count,'not found part1.'
		count+=1
		continue
	driver.find_element_by_id('companyDetail').click()
	locator = (By.XPATH,"//div[@class='list_l' and @style='display:block;']")
	try:
		WebDriverWait(driver,3).until(EC.presence_of_element_located(locator))
	except Exception as e:
		print count,'not found part1.'
		count+=1
		continue
	soup = BeautifulSoup(driver.page_source,'html.parser')
	table = soup.find('div',class_='list_l',style='display:block;')
	if not table:
		print "Occurred a loading error."
		continue
	tds = table.find_all('td',class_='')
	company_id = tds[1].string
	target = []
	for x in tds:
		if x.string:
			target.append(MySQLdb.escape_string(unicode(x.string).encode('utf8')))
		else:
			target.append('Null')
	cursor.execute(sentense1 % tuple(target))
	db.commit()



	locator = (By.XPATH,"//a[@onclick='changeTab();']")
	try:
		WebDriverWait(driver,3).until(EC.presence_of_element_located(locator))
	except Exception as e:
		print count,'not found part2.'
		count+=1
		continue
	point = driver.find_elements_by_xpath("//a[@onclick='changeTab();']")
	try:
		point[2].click()
	except Exception as e:
		print 'Occurred a loading error'
		continue
	locator = (By.XPATH,"//div[@class='list_l' and @style='display: block;']")
	try:
		WebDriverWait(driver,3).until(EC.presence_of_element_located(locator))
	except Exception as e:
		print count,'not found part2.'
		count+=1
		continue
	soup = BeautifulSoup(driver.page_source,'html.parser')
	table = soup.find('div',class_='list_l',style='display: block;')
	trs = table.find_all('tr')
	t = 1
	for x in trs:
		if t==1:
			t=0
			continue
		target = []
		tds = x.find_all('td')
		target.append(company_id)
		for y in tds:
			if y.string:
				target.append(MySQLdb.escape_string(unicode(y.string).encode('utf8')))
			else:
				target.append('Null')
		cursor.execute(sentense2 % tuple(target))
		db.commit()


	locator = (By.XPATH,"//a[@onclick='changeTab();']")
	try:
		WebDriverWait(driver,3).until(EC.presence_of_element_located(locator))
	except Exception as e:
		print count,'not found part3.'
		count+=1
		continue
	point = driver.find_elements_by_xpath("//a[@onclick='changeTab();']")
	try:
		point[3].click()
	except Exception as e:
		print 'Occurred a loading error'
		continue
	locator = (By.XPATH,"//div[@class='list_l' and @style='display: block;']")
	try:
		WebDriverWait(driver,3).until(EC.presence_of_element_located(locator))
	except Exception as e:
		print count,'not found part3.'
		count+=1
		continue
	soup = BeautifulSoup(driver.page_source,'html.parser')
	table = soup.find('div',class_='list_l',style='display: block;')
	tds = table.find_all('td',align='center')
	target = []
	target.append(company_id)
	for x in tds:
		if x.string:
			target.append(MySQLdb.escape_string(unicode(x.string).encode('utf8')))
		else:
			target.append('Null')
	cursor.execute(sentense3 % tuple(target))
	db.commit()
	
	print 'finish.',count
	count+=1
	if count>430760 and count < 830000:
		count=830760
	elif count>840000 and count < 870000:
		count=870000
```