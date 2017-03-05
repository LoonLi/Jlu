#coding="utf-8"
import redis
from pybloom import BloomFilter, ScalableBloomFilter  
import sys
sys.path.append("..")
import config
import re
import time
  
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

def make_dic(urls,depth):#make a dic set
    urls_set = []
    for url in urls:
        dic = {}
        dic['url'] =url
        dic['depth'] = depth
        urls_set.append(dic) 
    return urls_set


host_ip = config.host_ip
host_port = config.host_port
host_pass = config.host_pass
html_db = config.html_db
srq_db = config.srq_db
nrq_db = config.nrq_db
bl_db = config.bl_db # blacklist
tag_db = config.tag_db

max_depth = config.max_depth #the max parsing depth

start_urls = ['http://zsb.jlu.edu.cn/list/45.html']


nrq = RedisQueue('test',host=host_ip,port=host_port,db=nrq_db,password=host_pass)#have not solved queue
srq = RedisQueue('test',host=host_ip,port=host_port,db=srq_db,password=host_pass)#solved queue
trq = RedisQueue('test', host=host_ip,port=host_port,db=tag_db,password=host_pass)#set a tag to keep parallel
blacklist = redis.Redis(host=host_ip,port=host_port,db=bl_db,password=host_pass)#save the url costs too much time
bf = BloomFilter(capacity=1000000, error_rate=0.001)

if trq.empty():
    trq.put(0)

urls_dics = make_dic(start_urls,0)
for url in urls_dics:#put the urls to queue
    srq.put(url)


print 'Master start!'
start_time = time.time()
html_count = 0
averange_count=0
while True:
	if srq.empty() and nrq.empty():
		time.sleep(3)
		if srq.empty() and nrq.empty():
			print "Finished.Quit."
			cost_time = time.time()-start_time-3
			print 'it cost',cost_time
			averange_count=float(html_count)/cost_time
			print html_count,'has been parsed.In a speed of',averange_count,'/s.'
			break

	while True:
		if nrq.empty() != True:
			url_dic = eval(nrq.get())
			break
		time.sleep(0.2)
	
	try:
		url = url_dic['url']
		depth = int(url_dic['depth'])

		if depth>max_depth:
			print url,'depth is',depth,'.Stop parsing.'
			continue


		if blacklist.exists(url):
			print url,'is in blacklist.It used to cost',blacklist.get(url)
			continue
		if 'jlu.edu.' not in url:
			print url,"do not have jlu."
			continue

		reg = r'(\.([A-Za-z]{3}))$'
		result = re.search(reg,url)
		if result:
			if '.com' != result.group() or '.org' != result.group() or '.php' != result.group() or '.htm' != result.group():
				print url,'is not a website.'
				continue

		reg = r'(\.([A-Za-z]{4}))$'
		result = re.search(reg,url)
		if result:
			if '.html' != result.group():
				print url,'is not a website.'
				continue

		if  ';' in url or '(' in url or ')' in url:
			print url,'can not be solved.'
			continue	 	
		if bf.add(url):
			print url,"has been read."
			continue
		
		html_count+=1

		srq.put(url_dic)
		print url,'is put in queue.'
	except UnicodeError:
		pass

