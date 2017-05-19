---
layout: post
title:  "爬虫抓取网页中的url"
date:   2017-01-14 11:49:45 +0200
categories: python
published: true
---
	忙于考试没有写博客，现在总结一下之前做的一个爬虫。实现了抓取网页中的所有指向网页的url，当然可以自己定制想抓取的url格式。

## 0x00 预备内容

爬虫中用到了 **beautifulsoup** 来分析网页文本（这个包还可以用来做编码转换简直不能太好用）。用 **os** 来切割网页路径，用 **re** 做正则匹配。

## 0x01 爬虫代码

代码是这个样子的。

	class Spider:
		def __init__(self,turl):		
			self.url=turl
			self.response = urllib2.urlopen(self.url,timeout=5)
			self.html = self.response.read()
			self.outdegree = []
			reg = r'(http://.*?/)'
			select = re.compile(reg)
			self.domain = select.findall(self.url)[0][:-1]
			l = len(self.domain)
			t = list(self.domain)
			if self.domain[l-1]=='.':
				self.domain[l-1]='/'
			self.domain = "".join(self.domain)
		def parse_url(self):
			soup = BeautifulSoup(self.html,'html.parser')
			self.i = 0
			for link in soup.find_all('a'):
					tdomain = None
					string =  link.get('href')
					if string == None or string == '':
						string = '/'
					string = string.replace('\\','/')
					if string[0] == '#':
						string = '/'
					if string[0] == '.' or '/' not in string:
						t = os.path.split(self.url)
						tdomain = t[0]
						t = os.path.split(string)
						string = t[1]
					if 'http' in string:
						pass
					else:
						if tdomain:
							string = tdomain + '/' + string
						elif string[0]!= '/':
							string = self.domain+'/'+string
						else:
							string = self.domain+string
					self.outdegree.append(string)
					self.i+=1
					yield string

其中有统计网页的出度网页数目。麻烦的地方在与不同的网站根据程序员习惯不同，写的url格式五花八门，甚至有格式错误的，所以需要对这些url进行格式的处理。

url一般分成两种，绝对路径和相对路径。所以大思路是当rul是绝对路径时不做处理，直接返回；若是相对路径，需要在当前网页url域名下添加路径。

最需要注意的是对url细节上的处理。url还有可能是 *.jpg* 等图片文件，如果把这个url返回给urllib.urlopen的话，会卡住很长时间。所以还需要对url进行是否为网页的确认。

另外url还可能是javascript代码，也需要过滤。

虽然上述的过滤功能在这部分代码中都没有实现╮(╯_╰)╭。