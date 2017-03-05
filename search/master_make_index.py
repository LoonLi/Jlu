#coding=utf-8
import redis
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


words = redis.Redis(host=host_ip,port=host_port,db=wordtag_db) #词语对序号
index = redis.Redis(host=host_ip,port=host_port,db=index_db) #倒排索引
urltag = redis.Redis(host=host_ip,port=host_port,db=urltag_db,password=host_pass)

html = MySQLdb.connect(host_ip,mysql_user,mysql_passwd,mysql_db)

srq = RedisQueue('index', host = host_ip, port=host_port, db=srq_db,password=host_pass) #solved queue
nrq = RedisQueue('index', host = host_ip, port=host_port, db=nrq_db,password=host_pass) #have not solved queue

print 'Putting no. into queue...'
c = html.cursor()
sentence = "SELECT id,url FROM html"
c.execute(sentence)
data = c.fetchall()
html_counts = 0
for row in data:
    url_id = row[0]
    srq.put(url_id)
    html_counts+=1
print 'End putting.'

word_count = 0

print 'Putting dic to index...'
start_time = time.time()
while  True:
    if srq.empty() and nrq.empty():
        time.sleep(5)
        if srq.empty() and nrq.empty():
            print "Finished.Quit."
            cost_time = time.time()-start_time-5
            print 'It coast',cost_time 
            print html_counts,'context has been analysed.It is in a speed of',float(html_counts)/cost_time,'/s.'
            break

    while True:
        if nrq.empty() != True:
            dic_main = eval(nrq.get())
            break
        time.sleep(0.2)

    dic_words = dic_main['wordsdic']
    dic_url = dic_main['urldic']

    count = dic_url['url']

    for word in dic_words:
        if(words.exists(word)==False):#之前没有记录过这个词
            words.set(word,word_count)
            word_count=word_count+1
        no = words.get(word)
        index.hset(no,count,dic_words[word])

    print "HTML No.",count,"is finished."


