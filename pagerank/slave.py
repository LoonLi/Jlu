#coding="utf-8"
import redis
import time
from pybloom import BloomFilter, ScalableBloomFilter
import sys
import time
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

host_ip = config.host_ip
host_port = config.host_port
host_pass = config.host_pass
html_db = config.html_db
urltag_db = config.urltag_db
need_calc_db = config.need_calc_db
get_calc_db = config.get_calc_db
final_pagerank_db = config.final_pagerank_db

need_calc_que = RedisQueue('test', host = host_ip, port=host_port, db=need_calc_db,password=host_pass)
get_calc_que = RedisQueue('test', host = host_ip, port=host_port, db=get_calc_db,password=host_pass)

while True:
    if need_calc_que.empty():
        time.sleep(0.1)
        continue
    dic = eval(need_calc_que.get())
    tag_urls = dic['tag_urls']
    if not tag_urls:
        tag_value = 0
    else:
        tag_value = float(dic["vector_tag"])/len(tag_urls)
    r_dic = {}
    r_dic["tag_value"] = tag_value
    r_dic["tag_number"] = dic["tag_number"]
    get_calc_que.put(str(r_dic))
    print repr(r_dic),"is result."