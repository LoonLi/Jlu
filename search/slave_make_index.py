#coding=utf8
import redis
from bs4 import BeautifulSoup
import jieba
import MySQLdb
import time
import sys
sys.path.append("..")
import config

reload(sys)
sys.setdefaultencoding('utf-8')

class RedisQueue(object):  
    """Simple Queue with Redis Backend"""  
    def __init__(self, name, namespace='queue', **redis_kwargs):  
        """The default connection parameters are: host='localhost', port=6379, db=0"""  
        self.__db = redis.Redis(**redis_kwargs)  
        self.key = '%s:%s' %(namespace, name)  
  
    def qsize(self):  
        """Return the approximate size of the queue."""  
        return self.__db.llen(self.key)  
  
    def empty(self):  
        """Return True if the queue is empty, False otherwise."""  
        return self.qsize() == 0  
  
    def put(self, item):  
        """Put item into the queue."""  
        self.__db.rpush(self.key, item)  
  
    def get(self, block=True, timeout=None):  
        """Remove and return an item from the queue.  
 
        If optional args block is true and timeout is None (the default), block 
        if necessary until an item is available."""  
        if block:  
            item = self.__db.blpop(self.key, timeout=timeout)  
        else:  
            item = self.__db.lpop(self.key)  
  
        if item:  
            item = item[1]  
        return item  
  
    def get_nowait(self):  
        """Equivalent to get(False)."""  
        return self.get(False)


host_ip = config.host_ip
host_port = config.host_port
host_pass = config.host_pass
html_db = config.html_db
srq_db = config.srq_db
nrq_db = config.nrq_db
bl_db = config.bl_db # blacklist
tag_db = config.tag_db
wordtag_db = config.wordtag_db
index_db = config.index_db
urltag_db = config.urltag_db
mysql_user = config.mysql_user
mysql_passwd = config.mysql_passwd
mysql_db = config.mysql_db


rhtml = MySQLdb.connect(host_ip,mysql_user,mysql_passwd,mysql_db,charset='utf8')
words = redis.Redis(host=host_ip,port=host_port,db=wordtag_db) #词语对序号
index = redis.Redis(host=host_ip,port=host_port,db=index_db) #倒排索引

c = rhtml.cursor()
sentence = "SELECT html FROM html WHERE id='%s'"

srq = RedisQueue('index', host = host_ip, port=host_port, db=srq_db,password=host_pass) #solved queue
nrq = RedisQueue('index', host = host_ip, port=host_port, db=nrq_db,password=host_pass) #have not solved queue

count = 0 		#网页的编号
word_count = 0	#单词的编号
no = 0			#倒排索引的编号

while(True):
	# if nrq.empty() and srq.empty():
	# 	print "Complete!"
	# 	break
	while(True):
		if srq.empty() != True:#get a count
			count=srq.get()
			break
        time.sleep(0.2)
        # if nrq.empty() and srq.empty():
        #     print "Complete!"
        #     break
	dic_main = {}
	dic_url = {}
	dic_words = {}
	c.execute(sentence%(count))
	html = c.fetchone()
	soup=BeautifulSoup(html[0],'html.parser')
	string=soup.get_text()
	seg_list = jieba.cut_for_search(string) #分词
	for word in seg_list:
		if word not in dic_words:#这个词在索引中记录过
			dic_words[word] = 1
		else:
			dic_words[word]+=1
	dic_url['url'] = count
	dic_main['urldic']=dic_url
	dic_main['wordsdic']=dic_words
	nrq.put(dic_main)
	print "HTML No.",count,"is finished."
print 'end.\n'