#coding='utf-8'
from bs4 import BeautifulSoup
import urllib2
import redis
import MySQLdb
import re
import os


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



	def parse_html(self,no,rhtml,rurltag):
		sentence = """
		INSERT INTO html VALUES ('%d','%s','%s','%s','%d')
		"""
		print '1'
		c = rhtml.cursor()
		c.execute("set names utf8")
		rhtml.commit()
		print '2'
		try:
			c.execute(sentence%(no,MySQLdb.escape_string(self.url),MySQLdb.escape_string(self.html),MySQLdb.escape_string(str(self.outdegree)),self.i))
		except:
			soup = BeautifulSoup(self.html,'html.parser')
			self.html = unicode(soup).encode('utf8')
			c.execute(sentence%(no,MySQLdb.escape_string(self.url),MySQLdb.escape_string(self.html),MySQLdb.escape_string(str(self.outdegree)),self.i))
		rhtml.commit()
		print '3'
		rurltag.set(self.url,no)
		print self.url,'has benn saved.Its no. is ',no

