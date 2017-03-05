#coding="utf-8"
import redis
import time
from pybloom import BloomFilter, ScalableBloomFilter
import sys
import MySQLdb
sys.path.append("..")
import config
	
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

def make_square(html_db,urltag_db):
	tag = 0
	square = {}
	sentence = "SELECT id,url,outdegree_urls FROM html;"
	cursor = html_db.cursor()
	print 'Getting data from database...'
	cursor.execute(sentence)
	result = cursor.fetchall()
	print 'Gotten.'
	print 'Making url-no list.'
	urltag = {}
	for row in result:
		url_id = int(row[0])
		url = row[1]
		urltag[url]=url_id
	print 'Finished Making list.'
	for row in result:
		url_id = int(row[0])
		print url_id
		url = row[1]
		outdegree_urls = eval(row[2])
		outdegree_urls_numbers = []
		for x in outdegree_urls:
			if x in urltag:
				outdegree_urls_numbers.append(urltag[x])
		square[url_id] = outdegree_urls_numbers

	return square

	# while True:
	# 	if not html_db.exists(tag):
	# 		break
	# 	outdegree_urls = eval(html_db.hget(tag,"outdegree_urls"))
	# 	# true_outdegree_urls = []
	# 	# for x in outdegree_urls:
	# 	# 	if urltag_db.exists(x):
	# 	# 		true_outdegree_urls.append(int(urltag_db.get(x)))
	# 	true_outdegree_urls = html_db.hget(tag,"outdegree_counts")
	# 	if len(true_outdegree_urls) == 0:
	# 		true_outdegree_urls = ["NULL"]
	# 	square[tag] = true_outdegree_urls
	# 	print "Tag",tag,"Finished."
	# 	tag+=1
	# return square

host_ip = config.host_ip
host_port = config.host_port
host_pass = config.host_pass
html_db = config.html_db
urltag_db = config.urltag_db
need_calc_db = config.need_calc_db
get_calc_db = config.get_calc_db
final_pagerank_db = config.final_pagerank_db
mysql_user = config.mysql_user
mysql_passwd = config.mysql_passwd
mysql_db = config.mysql_db

need_calc_que = RedisQueue('test', host = host_ip, port=host_port, db=need_calc_db,password=host_pass)
get_calc_que = RedisQueue('test', host = host_ip, port=host_port, db=get_calc_db,password=host_pass)
html = MySQLdb.connect(host_ip,mysql_user,mysql_passwd,mysql_db)
urltag = redis.Redis(host=host_ip,port=host_port,db=urltag_db,password=host_pass)
final_pagerank = redis.Redis(host=host_ip,port=host_port,db=final_pagerank_db,password=host_pass)

start_time = time.time()

print "Start to make square......"
square = make_square(html,urltag)
print "Square has been built.Start to calculate PAGERANK."

print "Make original vector."
length = len(square)
origin = 1.0/length
vector = {}
print length
for i in square:
	vector[i]=origin
print "Original vector has benn built.It is",repr(vector)

for i in range(30):
	print "Now the calculate time is ---",i,"---"
	print "Begin to add tag to db."
	for x in square:
		dic = {}
		dic["vector_tag"] = vector[x]
		dic["tag_number"] = x
		dic["tag_urls"] = square[x]
		need_calc_que.put(str(dic))
	print "Finished adding."

	#calculate weighted vector
	for i in vector:
		vector[i] = vector[i]*0.3

	while True:
		if need_calc_que.empty() and get_calc_que.empty():
			time.sleep(1)
			if need_calc_que.empty() and get_calc_que.empty():
				break
		result_dic = eval(get_calc_que.get())
		tag_value = float(result_dic["tag_value"])
		tag_number = int(result_dic["tag_number"])
		outdegree_urls = square[tag_number]
		for x in outdegree_urls:
			vector[x]+=tag_value
	
	print "This turn finished.Vector is :"
	print repr(vector)


for x in vector:
	final_pagerank.set(x,vector[x])

cost_time = time.time()-start_time

print "Now finied."
print 'Cost',cost_time